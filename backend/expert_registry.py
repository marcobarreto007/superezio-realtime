"""
Expert Registry - Declarative registry of CODE experts for MoE system
Defines 10 specialized coding experts with their configurations
"""
from typing import Dict, List, Optional, TypedDict
from dataclasses import dataclass


class ExpertConfig(TypedDict):
    """Configuration for a single expert"""
    expert_id: str
    human_label: str
    description: str
    lora_adapter: Optional[str]  # LoRA adapter name or None for base model
    rag_domains: List[str]  # RAG namespaces to query
    default_tools: List[str]  # Default tools this expert can use
    keywords: List[str]  # Keywords that trigger this expert


# ============================================================================
# EXPERT REGISTRY - 10 CODE EXPERTS
# ============================================================================
EXPERTS: Dict[str, ExpertConfig] = {
    "code_general": {
        "expert_id": "code_general",
        "human_label": "General Code Expert",
        "description": "General programming, software architecture, design patterns, best practices",
        "lora_adapter": None,  # Uses base model
        "rag_domains": ["code_general"],
        "default_tools": ["read_file", "list_directory", "search_files", "get_file_info"],
        "keywords": ["code", "programming", "software", "develop", "architect", "design pattern"]
    },
    
    "code_python": {
        "expert_id": "code_python",
        "human_label": "Python Deep Expert",
        "description": "Python, FastAPI, Django, Flask, pandas, NumPy, PyTorch, pytest, type hints",
        "lora_adapter": "code_expert_v1",  # Will be trained
        "rag_domains": ["code_python", "code_general"],
        "default_tools": ["read_file", "write_file", "search_files", "list_directory", "create_directory"],
        "keywords": [
            "python", "fastapi", "django", "flask", "pandas", "numpy", "pytorch",
            "pip", "venv", "requirements.txt", "def ", ".py", "pytest",
            "__init__", "import ", "class ", "async def"
        ]
    },
    
    "code_ts": {
        "expert_id": "code_ts",
        "human_label": "TypeScript/Node Expert",
        "description": "TypeScript, JavaScript, React, Next.js, Node.js, Express, Vite, npm, pnpm",
        "lora_adapter": "code_expert_v1",  # Same LoRA, different RAG context
        "rag_domains": ["code_ts", "code_general"],
        "default_tools": ["read_file", "write_file", "search_files", "list_directory", "create_directory"],
        "keywords": [
            "typescript", "javascript", "react", "next.js", "nextjs", "node", "nodejs",
            "npm", "pnpm", "yarn", "vite", "tsx", "jsx", ".ts", ".tsx", ".js",
            "tsconfig", "package.json", "express", "interface ", "type ", "const "
        ]
    },
    
    "code_infra": {
        "expert_id": "code_infra",
        "human_label": "Infrastructure/DevOps Expert",
        "description": "Docker, Kubernetes, CI/CD, GitHub Actions, Terraform, Helm, docker-compose",
        "lora_adapter": "code_expert_v1",
        "rag_domains": ["code_infra", "code_general"],
        "default_tools": ["read_file", "write_file", "search_files", "list_directory"],
        "keywords": [
            "docker", "dockerfile", "docker-compose", "kubernetes", "k8s", "helm",
            "ci/cd", "github actions", "gitlab ci", "terraform", "ansible",
            "deployment", "container", "pod", "service", "ingress", "yaml"
        ]
    },
    
    "code_ml": {
        "expert_id": "code_ml",
        "human_label": "ML/AI Expert",
        "description": "Machine Learning, LLMs, LoRA, transformers, Qwen, GPU optimization, training",
        "lora_adapter": "code_expert_v1",
        "rag_domains": ["code_ml", "code_python", "code_general"],
        "default_tools": ["read_file", "write_file", "search_files", "list_directory"],
        "keywords": [
            "lora", "qwen", "transformers", "huggingface", "pytorch", "tensorflow",
            "gpu", "cuda", "vram", "model", "training", "fine-tuning", "finetune",
            "attention", "embedding", "checkpoint", "adapter", "peft", "qlora",
            "llamafactory", "inference", "tokenizer"
        ]
    },
    
    "code_database": {
        "expert_id": "code_database",
        "human_label": "Database Expert",
        "description": "SQL, PostgreSQL, MongoDB, Redis, ORMs, database design, migrations",
        "lora_adapter": "code_expert_v1",
        "rag_domains": ["code_database", "code_general"],
        "default_tools": ["read_file", "write_file", "search_files"],
        "keywords": [
            "sql", "postgresql", "postgres", "mysql", "mongodb", "redis",
            "database", "orm", "sqlalchemy", "prisma", "mongoose",
            "migration", "schema", "query", "index", "table"
        ]
    },
    
    "code_frontend": {
        "expert_id": "code_frontend",
        "human_label": "Frontend Expert",
        "description": "React, Vue, CSS, Tailwind, UI/UX, responsive design, state management",
        "lora_adapter": "code_expert_v1",
        "rag_domains": ["code_frontend", "code_ts", "code_general"],
        "default_tools": ["read_file", "write_file", "search_files", "list_directory"],
        "keywords": [
            "react", "vue", "svelte", "css", "tailwind", "styled-components",
            "component", "hook", "useState", "useEffect", "redux", "zustand",
            "ui", "ux", "responsive", "mobile", "flexbox", "grid"
        ]
    },
    
    "code_api": {
        "expert_id": "code_api",
        "human_label": "API Design Expert",
        "description": "REST APIs, GraphQL, OpenAPI, webhooks, authentication, rate limiting",
        "lora_adapter": "code_expert_v1",
        "rag_domains": ["code_api", "code_general"],
        "default_tools": ["read_file", "write_file", "search_files"],
        "keywords": [
            "api", "rest", "graphql", "endpoint", "route", "openapi", "swagger",
            "webhook", "auth", "jwt", "oauth", "rate limit", "cors",
            "middleware", "request", "response"
        ]
    },
    
    "code_testing": {
        "expert_id": "code_testing",
        "human_label": "Testing Expert",
        "description": "Unit tests, integration tests, E2E, pytest, Jest, mocking, TDD",
        "lora_adapter": "code_expert_v1",
        "rag_domains": ["code_testing", "code_general"],
        "default_tools": ["read_file", "write_file", "search_files", "list_directory"],
        "keywords": [
            "test", "testing", "pytest", "jest", "unittest", "mock", "fixture",
            "tdd", "bdd", "e2e", "integration test", "unit test",
            "coverage", "assert", "expect", "describe", "it("
        ]
    },
    
    "code_algorithms": {
        "expert_id": "code_algorithms",
        "human_label": "Algorithms Expert",
        "description": "Data structures, algorithms, optimization, complexity analysis, leetcode",
        "lora_adapter": "code_expert_v1",
        "rag_domains": ["code_algorithms", "code_general"],
        "default_tools": ["read_file", "write_file"],
        "keywords": [
            "algorithm", "data structure", "complexity", "big o", "optimization",
            "leetcode", "binary search", "dynamic programming", "graph",
            "tree", "heap", "hash", "sort", "recursion"
        ]
    },
    
    "code_hf_curator": {
        "expert_id": "code_hf_curator",
        "human_label": "HuggingFace Curator",
        "description": "HuggingFace Hub specialist: choosing models, comparing datasets, open-source models, model cards, weights, checkpoints",
        "lora_adapter": None,  # Uses base model with RAG
        "rag_domains": ["hf_models_code", "hf_datasets_code"],
        "default_tools": ["read_file", "list_directory", "search_files"],
        "keywords": [
            # HuggingFace Hub
            "huggingface", "hugging face", "hf hub", "hf_hub", "hf",
            "hf token", "hf cache", "hf_models", "hf_datasets",
            "hf catalog", "hf harvester", "transformers hub",
            "modelo do hf", "modelos do hf", "datasets do hf",
            
            # Specific Models
            "bigcode", "the stack", "the-stack", "starcoder", "starcoder2", "starcoder 2",
            "codellama", "code llama", "code-llama",
            "qwen2.5", "qwen 2.5", "qwen2", "qwen 2", "qwen code", "qwencoder",
            "mistral", "mixtral", "llama", "llama 2", "llama 3", "llama3", "llama2",
            "wizard coder", "wizardcoder", "deepseek", "deepseek-coder",
            
            # Model artifacts
            "checkpoint", "weights", "safetensors", "gguf", "ggml",
            "adapter", "lora weights", "model file", "model weights",
            
            # Model selection queries
            "open-source model", "open source model", "modelo open source",
            "modelo open-source", "opensource model",
            "melhor modelo de código", "best code model", "best model for code",
            "escolher modelo", "qual modelo usar", "which model should i use",
            "which model is better", "compare models", "model comparison",
            "recomendar modelo", "recommend model", "model recommendation",
            
            # General ML model queries
            "model card", "dataset card", "code model", "code dataset",
            "pretrained model", "pre-trained model", "foundation model",
            "llm for code", "code llm", "coding model"
        ]
    },

    "crew_agent_orchestrator": {
        "expert_id": "crew_agent_orchestrator",
        "human_label": "Autonomous Agent Orchestrator",
        "description": "Handles complex, multi-step projects by assembling and managing a team of AI agents (CrewAI).",
        "lora_adapter": None,
        "rag_domains": ["code_general", "code_python", "code_ts", "code_infra", "code_api"],
        "default_tools": ["read_file", "write_file", "list_directory", "search_files", "move_mouse_to", "click_at", "type_text", "take_screenshot"],
        "keywords": [
            "create a project", "build an app", "develop a new feature", "end-to-end",
            "do it for me", "autonomously", "handle the whole process",
            "crie um projeto", "construa uma aplicação", "de ponta a ponta",
            "faça por mim", "autonomamente", "cuide de todo o processo",
            "web search and report", "pesquise na web e me entregue um relatório"
        ]
    }
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_expert(expert_id: str) -> ExpertConfig:
    """
    Get expert configuration by ID.
    
    Args:
        expert_id: Expert identifier (e.g. "code_python")
        
    Returns:
        ExpertConfig dictionary
        
    Raises:
        ValueError: If expert_id not found
    """
    if expert_id not in EXPERTS:
        raise ValueError(
            f"Expert '{expert_id}' not found. "
            f"Available: {list(EXPERTS.keys())}"
        )
    return EXPERTS[expert_id]


def list_experts() -> List[ExpertConfig]:
    """
    List all available experts.
    
    Returns:
        List of all expert configurations
    """
    return list(EXPERTS.values())


def resolve_from_hint(hint: str) -> str:
    """
    Resolve an expert ID from a hint string.
    Maps common aliases to expert IDs.
    
    Args:
        hint: Hint string (e.g. "python", "typescript", "docker")
        
    Returns:
        Expert ID (e.g. "code_python")
        Falls back to "code_general" if no match
    """
    hint_lower = hint.lower().strip()
    
    # Direct mapping
    hint_to_expert = {
        "python": "code_python",
        "py": "code_python",
        "typescript": "code_ts",
        "ts": "code_ts",
        "javascript": "code_ts",
        "js": "code_ts",
        "react": "code_frontend",
        "node": "code_ts",
        "docker": "code_infra",
        "kubernetes": "code_infra",
        "k8s": "code_infra",
        "ml": "code_ml",
        "ai": "code_ml",
        "database": "code_database",
        "db": "code_database",
        "sql": "code_database",
        "api": "code_api",
        "test": "code_testing",
        "testing": "code_testing",
        "algorithm": "code_algorithms",
        "algo": "code_algorithms",
        "frontend": "code_frontend",
        "ui": "code_frontend"
    }
    
    if hint_lower in hint_to_expert:
        return hint_to_expert[hint_lower]
    
    # Check if hint matches any expert_id directly
    if hint_lower in EXPERTS:
        return hint_lower
    
    # Fallback
    return "code_general"


def get_superezio_code_persona() -> str:
    """
    Returns SuperEzio-Code persona for all code experts.
    This defines WHO SuperEzio is when working with code.
    
    Returns:
        SuperEzio-Code persona string
    """
    return """Você é o SuperEzio-Code, o maior especialista do mundo em programação e arquitetura de sistemas.

IDENTIDADE:
- Você é uma IA construída pelo Marco Barreto para ser o cérebro técnico do projeto Superezio.
- Seu foco principal é: código, arquitetura, automação e estudo contínuo.
- Você se vê como uma "máquina de estudo" que nunca para de aprender, organizar e explicar.

ESPECIALIZAÇÃO:
- Você domina profundamente: Python, TypeScript/JavaScript, Bash, PowerShell, Docker, Git, FastAPI, React/Vite, IA (PyTorch, modelos de linguagem, RAG, LoRA, LLaMA-Factory, APIs de LLM).
- Você é capaz de pegar uma ideia vaga e entregar:
  - arquitetura completa,
  - código funcional,
  - scripts de automação (CMD/PowerShell),
  - e explicação passo a passo.

ESTILO DE RESPOSTA:
- Fale em português coloquial, direto, sem floreio.
- Seja cético: questione premissas se algo não fizer sentido.
- Prefira sempre:
  1) visão geral,
  2) arquitetura,
  3) código completo,
  4) como executar (comandos),
  5) como evoluir / estudar mais.
- Quando gerar código, priorize:
  - exemplos completos (arquivo inteiro),
  - instruções de execução para Windows (CMD/PowerShell),
  - comentários explicando o PORQUÊ das escolhas (não só o "o que").

COMPORTAMENTO DE EXPERT:
- Se o pedido for de código, você assume que é responsável por toda a pipeline: design → implementação → execução.
- Se algo estiver ambíguo, você escolhe um caminho sensato e deixa claro o que assumiu.
- Se houver risco de bug conceitual, você corrige na raiz (arquitetura), não só "remenda".
- Quando não tiver certeza, você:
  - diz o que é fato,
  - diz o que é suposição,
  - sugere como validar na prática.

MÁQUINA DE ESTUDO:
- Sempre que possível, você transforma a resposta em aprendizado:
  - sugere exercícios,
  - mostra variações melhores,
  - indica como generalizar aquele código para projetos maiores.
- Você pensa em "engenharia de longo prazo": código limpo, extensível e fácil de refatorar.

PRIORIDADES:
1) Segurança e limites da plataforma.
2) Correção técnica.
3) Clareza máxima.
4) Código executável com o mínimo de atrito.
5) Tornar o usuário mais forte como programador a cada resposta.
"""


def get_expert_persona(expert_id: str) -> str:
    """
    Generate expert persona prompt for a given expert.
    For code_* experts, includes SuperEzio-Code persona.
    
    Args:
        expert_id: Expert identifier
        
    Returns:
        Persona prompt string
    """
    expert = get_expert(expert_id)
    
    # For code experts, inject SuperEzio-Code persona first
    if expert_id.startswith("code_"):
        persona = get_superezio_code_persona() + "\n\n"
        persona += f"""[MODO EXPERT: {expert['human_label']}]

Especialização atual: {expert['description']}

EXPERTISE FOCUS:
- Provide deep, idiomatic solutions in your specialty
- Reference best practices and modern patterns
- Write production-ready, maintainable code
- Consider edge cases and error handling

AVAILABLE TOOLS:
You have access to these tools: {', '.join(expert['default_tools'])}
ALWAYS use these tools to inspect files, list directories, or search before making assumptions.

NEVER hallucinate file contents - read them first with read_file.
NEVER guess directory structure - list it first with list_directory.
"""
    else:
        # Non-code experts use original persona
        persona = f"""You are {expert['human_label']}, specialized in: {expert['description']}.

EXPERTISE FOCUS:
- Provide deep, idiomatic solutions in your specialty
- Reference best practices and modern patterns
- Write production-ready, maintainable code
- Consider edge cases and error handling

AVAILABLE TOOLS:
You have access to these tools: {', '.join(expert['default_tools'])}
ALWAYS use these tools to inspect files, list directories, or search before making assumptions.

NEVER hallucinate file contents - read them first with read_file.
NEVER guess directory structure - list it first with list_directory.

STYLE:
- Be direct and practical
- Show code examples when helpful
- Explain complex concepts clearly
- Use proper terminology from your domain"""
    
    return persona
