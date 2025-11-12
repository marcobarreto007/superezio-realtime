# File: scripts/build_canada_accounting_corpus.py
# Python >= 3.10
"""
SETUP RÁPIDO (uma vez):
  pip install requests beautifulsoup4 lxml pdfminer.six tiktoken unidecode tqdm

USO:
  python build_canada_accounting_corpus.py --out ../data/cra_corpus.jsonl --max-pages 1200

REM (por quê): foca só em fontes públicas sob OGL/Reproduction Order para evitar corpus "contaminado".
"""

from __future__ import annotations
import re, os, sys, time, json, math, hashlib, argparse, html, io
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urldefrag, urlparse
from collections import deque
import requests
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text as pdf_extract
from unidecode import unidecode
from tqdm import tqdm

# ---- Config base ----
WHITELIST_DOMAINS = {
    "www.canada.ca", "canada.ca",
    "laws-lois.justice.gc.ca",
    "open.canada.ca",
    "gazette.gc.ca",
    "www.osfi-bsif.gc.ca", "osfi-bsif.gc.ca",
    "www150.statcan.gc.ca", "www.statcan.gc.ca", "statcan.gc.ca",
    "a2aj.ca", "huggingface.co",
}

SEEDS = [
    # CRA tech + guias
    "https://www.canada.ca/en/revenue-agency/services/tax/technical-information/income-tax/income-tax-folios-index.html",
    "https://www.canada.ca/en/revenue-agency/services/tax/technical-information/technical-information-gst-hst/gst-hst-memoranda-series.html",
    "https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/t4001.html",
    "https://www.canada.ca/en/revenue-agency/services/forms-publications/payroll/t4032-payroll-deductions-tables.html",
    "https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/t4012/t2-corporation-income-tax-guide.html",
    # Leis (Justice Laws)
    "https://laws-lois.justice.gc.ca/eng/acts/I-3.3/index.html",  # Income Tax Act
    "https://laws-lois.justice.gc.ca/eng/acts/E-15/index.html",   # Excise Tax Act
    "https://laws-lois.justice.gc.ca/eng/regulations/si-97-5/page-1.html",  # Reproduction of Federal Law Order
    # Gazette
    "https://gazette.gc.ca/rp-pr/p1/2025/index-eng.html",
    # Finance Canada (Budget Annexes 2025)
    "https://budget.canada.ca/2025/report-rapport/anx1-en.html",
    # OSFI guidance
    "https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/ifrs-17-insurance-contracts-guideline",
    "https://www.osfi-bsif.gc.ca/en/guidance/guidance-library",
    # StatCan docs (licença aberta)
    "https://www.statcan.gc.ca/en/terms-conditions/open-licence",
    "https://www150.statcan.gc.ca/n1/pub/62f0014m/62f0014m2025007-eng.htm",  # ASPI 2025
    # A2AJ (datasets abertos legais)
    "https://a2aj.ca/canadian-legal-data/",
    "https://huggingface.co/datasets/a2aj/canadian-case-law",
    # OGL (licença)
    "https://open.canada.ca/en/open-government-licence-canada",
]

# Mapeia licença presumida por domínio
def infer_license(url: str) -> str:
    host = urlparse(url).netloc
    if host.endswith("justice.gc.ca"):
        return "Reproduction of Federal Law Order (SI/97-5)"
    if "statcan.gc.ca" in host:
        return "Statistics Canada Open Licence"
    if "open.canada.ca" in host or "canada.ca" in host or "gc.ca" in host:
        return "Open Government Licence – Canada"
    if "osfi-bsif.gc.ca" in host:
        return "Open Government Licence – Canada"
    if "huggingface.co" in host or "a2aj.ca" in host:
        return "Project-specific open terms (verify repo/dataset page)"
    return "Unknown/verify"

# Extrai texto "limpo" de HTML
def html_to_text(url: str, content: bytes) -> str:
    soup = BeautifulSoup(content, "lxml")
    # remove navegação
    for tag in soup(["script", "style", "nav", "header", "footer", "form", "noscript"]):
        tag.decompose()
    # remove elementos óbvios de boilerplate
    for cls in ["breadcrumb", "gc-subway", "gcweb-menu", "pagedetails", "wb-share"]:
        for t in soup.select(f".{cls}"):
            t.decompose()
    text = soup.get_text("\n", strip=True)
    # normaliza
    text = html.unescape(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

# Extrai texto de PDF
def pdf_to_text(raw: bytes) -> str:
    with io.BytesIO(raw) as bio:
        try:
            return pdf_extract(bio)
        except Exception:
            return ""

def is_allowed(url: str) -> bool:
    u = urlparse(url)
    if u.scheme not in ("http", "https"):
        return False
    host = u.netloc.lower()
    return any(host.endswith(d) or host == d for d in WHITELIST_DOMAINS)

def canonicalize(base: str, link: str) -> str:
    u = urljoin(base, link)
    u, _frag = urldefrag(u)
    return u

def should_visit(url: str) -> bool:
    path = urlparse(url).path.lower()
    # ignora mídias grandes, anexos não textuais
    if any(path.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico", ".zip", ".rar")):
        return False
    return True

@dataclass
class Doc:
    id: str
    url: str
    title: str
    text: str
    source: str
    license: str
    retrieved_at: float

def hash_id(text: str, url: str) -> str:
    h = hashlib.sha256()
    h.update(url.encode("utf-8"))
    h.update(b"\n")
    h.update(text.encode("utf-8"))
    return h.hexdigest()[:16]

def chunk_text(text: str, max_chars: int = 5000) -> list[str]:
    # corta por seções/cabeçalhos quando possível
    parts = re.split(r"\n(?=[A-Z][^\n]{0,120}\n[-=]{2,}|#{1,6}\s)", text)
    chunks = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) <= max_chars:
            chunks.append(p)
        else:
            # fallback duro por parágrafos
            paras = [pp.strip() for pp in p.split("\n") if pp.strip()]
            buf = ""
            for para in paras:
                if len(buf) + len(para) + 1 <= max_chars:
                    buf += ("\n" if buf else "") + para
                else:
                    if buf:
                        chunks.append(buf)
                    buf = para
            if buf:
                chunks.append(buf)
    return chunks

def fetch(session: requests.Session, url: str, timeout=25) -> tuple[bytes, str]:
    r = session.get(url, timeout=timeout, headers={"User-Agent": "SuperEzio-CorpusBuilder/1.0"})
    r.raise_for_status()
    ctype = r.headers.get("Content-Type", "").lower()
    return r.content, ctype

def crawl(seeds: list[str], max_pages: int, out_jsonl: str):
    seen: set[str] = set()
    q = deque(seeds)
    docs: list[Doc] = []
    session = requests.Session()

    pbar = tqdm(total=max_pages, desc="🇨🇦 Crawling CRA & Gov Docs")
    while q and len(seen) < max_pages:
        url = q.popleft()
        if not is_allowed(url) or not should_visit(url):
            continue
        if url in seen:
            continue
        seen.add(url)
        try:
            raw, ctype = fetch(session, url)
        except Exception as e:
            print(f"❌ Erro em {url}: {e}")
            continue

        text = ""
        title = ""
        if "pdf" in ctype or url.lower().endswith(".pdf"):
            text = pdf_to_text(raw)
        elif "html" in ctype or "xml" in ctype or url.endswith("/"):
            text = html_to_text(url, raw)
        else:
            continue

        # título simples
        if not title:
            m = re.search(r"^(.{10,120})$", text, flags=re.MULTILINE)
            title = (m.group(1).strip() if m else url)

        text = unidecode(text)
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"\n{2,}", "\n\n", text)

        if len(text) > 400:
            lic = infer_license(url)
            # chunk e grava
            for ck in chunk_text(text, max_chars=4800):
                doc = Doc(
                    id=hash_id(ck, url),
                    url=url,
                    title=title[:120],
                    text=ck,
                    source=urlparse(url).netloc,
                    license=lic,
                    retrieved_at=time.time(),
                )
                docs.append(doc)

        # descobre novos links (somente HTML)
        if "html" in ctype:
            try:
                soup = BeautifulSoup(raw, "lxml")
                for a in soup.find_all("a", href=True):
                    nxt = canonicalize(url, a["href"])
                    if is_allowed(nxt) and should_visit(nxt) and nxt not in seen:
                        q.append(nxt)
            except Exception:
                pass

        pbar.update(1)
    pbar.close()

    # dedup por hash do conteúdo
    uniq = {}
    for d in docs:
        if d.id not in uniq:
            uniq[d.id] = d

    os.makedirs(os.path.dirname(out_jsonl) or ".", exist_ok=True)
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for d in uniq.values():
            f.write(json.dumps(asdict(d), ensure_ascii=False) + "\n")

    print(f"\n✅ Gravado {len(uniq)} documentos em {out_jsonl}")

def convert_to_lora_format(in_jsonl: str, out_jsonl: str):
    """
    Converte Doc -> formato LoRA training (messages format)
    """
    out = []
    with open(in_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            title = d.get("title", "")
            url = d.get("url", "")
            text = d.get("text", "")
            
            # Formato messages para LoRA
            item = {
                "messages": [
                    {
                        "role": "system",
                        "content": "Você é SuperEzio, um CPA canadense expert. Use apenas informações oficiais do governo canadense."
                    },
                    {
                        "role": "user",
                        "content": f"Explique sobre: {title}"
                    },
                    {
                        "role": "assistant",
                        "content": text + f"\n\nFonte: {url}"
                    }
                ]
            }
            out.append(item)

    with open(out_jsonl, "w", encoding="utf-8") as f:
        for it in out:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"✅ LoRA dataset salvo em {out_jsonl} ({len(out)} exemplos)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../data/cra_corpus.jsonl")
    ap.add_argument("--max-pages", type=int, default=800)
    ap.add_argument("--lora-out", default="../data/cra_training.jsonl")
    args = ap.parse_args()

    print("🚀 Iniciando crawl de fontes oficiais canadenses...")
    crawl(SEEDS, args.max_pages, args.out)
    
    if args.lora_out:
        print("\n📝 Convertendo para formato LoRA...")
        convert_to_lora_format(args.out, args.lora_out)

if __name__ == "__main__":
    main()
