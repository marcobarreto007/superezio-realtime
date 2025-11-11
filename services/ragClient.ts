// Simple client-side RAG: builds an embedding index from URLs
// Uses Ollama embeddings via Vite proxy to avoid CORS

type Embedding = number[];

type DocChunk = {
  id: string;
  url: string;
  content: string;
  embedding: Embedding;
};

const EMBEDDING_MODEL = (process.env.EMBEDDING_MODEL as string) || 'nomic-embed-text:latest';
const OLLAMA_BASE_URL = (process.env.OLLAMA_BASE_URL as string) || '/ollama';

const state: { index: DocChunk[] | null } = { index: null };

async function embed(texts: string[]): Promise<Embedding[]> {
  const base = OLLAMA_BASE_URL.trim();
  const url = base.endsWith('.php') ? `${base}?path=/api/embeddings` : `${base}/api/embeddings`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: EMBEDDING_MODEL, input: texts }),
  });
  if (!res.ok) throw new Error('Failed to get embeddings');
  const data = await res.json();
  return data.embeddings as Embedding[];
}

function chunkText(text: string, size = 800, overlap = 120): string[] {
  const words = text.split(/\s+/);
  const chunks: string[] = [];
  let i = 0;
  while (i < words.length) {
    const chunk = words.slice(i, i + size).join(' ');
    if (chunk.trim()) chunks.push(chunk);
    i += size - overlap;
  }
  return chunks;
}

export async function ensureIndex() {
  if (state.index) return;
  // Bootstrap with README as a default doc so RAG has context
  const urls = ['/README.md'];
  const docs: { url: string; content: string }[] = [];
  for (const url of urls) {
    try {
      const res = await fetch(url);
      if (!res.ok) continue;
      const content = await res.text();
      docs.push({ url, content });
    } catch (_) {
      // ignore
    }
  }
  const allChunks: { url: string; content: string }[] = [];
  for (const d of docs) {
    const chunks = chunkText(d.content).map((c) => ({ url: d.url, content: c }));
    allChunks.push(...chunks);
  }
  if (allChunks.length === 0) {
    state.index = [];
    return;
  }
  const embeddings = await embed(allChunks.map((c) => c.content));
  state.index = allChunks.map((c, i) => ({
    id: `${c.url}#${i}`,
    url: c.url,
    content: c.content,
    embedding: embeddings[i],
  }));
}

function cosineSim(a: Embedding, b: Embedding) {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb) + 1e-8);
}

export async function retrieve(query: string, k = 4) {
  await ensureIndex();
  if (!state.index || state.index.length === 0) return [] as DocChunk[];
  const [qEmb] = await embed([query]);
  return [...state.index]
    .map((c) => ({ c, score: cosineSim(qEmb, c.embedding) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, k)
    .map((x) => x.c);
}
