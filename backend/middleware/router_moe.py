"""
MoE Router - Classificação automática de intenção
Detecta qual especialista deve responder baseado no texto de entrada
"""

import re
from typing import Dict, List, Tuple

# Palavras-chave por especialista
EXPERT_KEYWORDS = {
    "familia": [
        # Nomes de família
        "rapha", "raphael", "ana paula", "marco", "barreto", "familia", "pai", "filho", "mae", "irmao",
        # Relações
        "parente", "primo", "tio", "tia", "avo", "neto",
        # Eventos familiares
        "aniversario", "natal", "pascoa", "ferias", "viagem", "passeio",
        # Emoções e rotina
        "amor", "carinho", "saudade", "orgulho", "feliz", "triste",
        "escola", "universidade", "udem", "montreal", "faculdade",
        # Hobbies específicos da família
        "oilers", "hockey", "sushi", "league of legends", "lol", "game"
    ],
    
    "contabilidade": [
        # Impostos
        "icms", "irpf", "irpj", "pis", "cofins", "iss", "ipi", "imposto", "tributo", "taxa",
        # CRA e contabilidade canadense
        "cra", "t1", "t4", "rrsp", "tfsa", "gst", "hst", "qst",
        # Termos contábeis
        "declaracao", "balanco", "contabilidade", "fiscal", "receita", "despesa",
        "lucro", "prejuizo", "nota fiscal", "nf-e", "sped", "ecf",
        # Empresas e negócios
        "empresa", "cnpj", "mei", "ltda", "s.a.", "simples nacional",
        "regime tributario", "apuracao", "guia", "darf", "dare"
    ],
    
    "trafego": [
        # Projeto específico
        "miovision", "trafficai", "camera", "deteccao", "detection",
        # Tráfego e mobilidade
        "trafego", "transito", "veiculo", "carro", "moto", "onibus",
        "semaforo", "cruzamento", "via", "avenida", "rua",
        # Tecnologia de visão
        "yolo", "opencv", "video", "frame", "bbox", "tracking",
        "neural", "deep learning", "computer vision", "ia", "ml"
    ],
    
    "pessoal": [
        # Saúde e bem-estar
        "saude", "medico", "hospital", "doente", "dor", "remedio",
        "exame", "consulta", "tratamento", "sintoma",
        # Vida no Canadá
        "canada", "quebec", "imigracao", "visto", "residencia permanente",
        "cidadania", "csq", "trabalho", "emprego", "entrevista",
        # Sentimentos pessoais
        "ansioso", "preocupado", "cansado", "estressado", "nervoso",
        "confiante", "motivado", "desanimado", "frustrado"
    ]
}

# Pesos para cálculo de score
KEYWORD_WEIGHT = 1.0
EXACT_MATCH_BONUS = 2.0
PHRASE_BONUS = 1.5


def normalize_text(text: str) -> str:
    """Normaliza texto para comparação"""
    text = text.lower()
    # Remove acentos comuns
    replacements = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ü': 'u',
        'ç': 'c'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def calculate_expert_score(text: str, keywords: List[str]) -> float:
    """Calcula score de relevância para um especialista"""
    text_norm = normalize_text(text)
    score = 0.0
    
    for keyword in keywords:
        keyword_norm = normalize_text(keyword)
        
        # Match exato de palavra completa
        pattern = r'\b' + re.escape(keyword_norm) + r'\b'
        matches = len(re.findall(pattern, text_norm))
        if matches > 0:
            score += EXACT_MATCH_BONUS * matches
        
        # Match parcial (substring)
        elif keyword_norm in text_norm:
            score += KEYWORD_WEIGHT
    
    return score


def infer_expert(text: str) -> str:
    """
    Detecta qual especialista deve responder baseado no texto
    
    Returns:
        str: 'familia', 'contabilidade', 'trafego', 'pessoal', ou 'geral'
    """
    if not text or len(text.strip()) < 3:
        return "geral"
    
    scores: Dict[str, float] = {}
    
    # Calcular score para cada especialista
    for expert, keywords in EXPERT_KEYWORDS.items():
        scores[expert] = calculate_expert_score(text, keywords)
    
    # Encontrar especialista com maior score
    max_score = max(scores.values())
    
    # Se nenhum especialista teve score significativo, usar geral
    if max_score < KEYWORD_WEIGHT:
        return "geral"
    
    # Retornar especialista com maior score
    best_expert = max(scores.items(), key=lambda x: x[1])[0]
    
    return best_expert


def get_expert_info(expert: str) -> Dict[str, str]:
    """Retorna informações sobre um especialista"""
    info = {
        "familia": {
            "name": "Família",
            "description": "Informações sobre família, parentes, rotina familiar",
            "lora": "familia",
            "rag_namespace": "familia"
        },
        "contabilidade": {
            "name": "Contabilidade",
            "description": "Impostos, CRA, contabilidade canadense, empresas",
            "lora": "contabilidade",
            "rag_namespace": "contabilidade"
        },
        "trafego": {
            "name": "Tráfego",
            "description": "MIovision, TrafficAI, detecção de veículos, câmeras",
            "lora": "trafego",
            "rag_namespace": "trafego"
        },
        "pessoal": {
            "name": "Pessoal",
            "description": "Saúde, vida no Canadá, trabalho, sentimentos",
            "lora": None,
            "rag_namespace": "vida_pessoal"
        },
        "geral": {
            "name": "Geral",
            "description": "Conhecimento geral, fallback padrão",
            "lora": None,
            "rag_namespace": None
        }
    }
    return info.get(expert, info["geral"])


def test_router():
    """Testes básicos do router"""
    test_cases = [
        ("Quem é o Rapha?", "familia"),
        ("Como está a Ana Paula?", "familia"),
        ("Quanto é o ICMS no Canadá?", "contabilidade"),
        ("Preciso declarar IRPF", "contabilidade"),
        ("Como funciona o MIovision?", "trafego"),
        ("Detecção de veículos na câmera", "trafego"),
        ("Estou me sentindo ansioso", "pessoal"),
        ("Como está o tempo hoje?", "geral"),
        ("Oilers ganhou ontem?", "familia"),
        ("Deadline da T1 no CRA", "contabilidade")
    ]
    
    print("\n" + "="*80)
    print("🧪 TESTE DO MOE ROUTER")
    print("="*80)
    
    correct = 0
    for text, expected in test_cases:
        result = infer_expert(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{text[:50]}' -> {result} (esperado: {expected})")
        if result == expected:
            correct += 1
    
    accuracy = (correct / len(test_cases)) * 100
    print(f"\n📊 Acurácia: {correct}/{len(test_cases)} ({accuracy:.1f}%)")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_router()
