import { getOllamaBaseUrl, getOllamaModel } from '@/config/env';
import { Message } from '@/types';
import { ragService } from './ragService';
import { getWeather, getCryptoPrice, formatWeatherInfo, formatCryptoInfo } from './externalAPIs';
import { agentService } from './agentService';

const SYSTEM_PROMPT = `Você é SuperEzio, uma IA assistente com personalidade marcante.

PERSONALIDADE E ESTILO:
- Comunicação DIRETA, coloquial e sem floreios, em português do Brasil
- Levemente cético, pragmático e NÃO bajula o usuário
- Respostas OBJETIVAS, focadas e eficientes
- NÃO faça perguntas casuais desnecessárias (clima, como está, etc)
- NÃO seja excessivamente verboso ou empolgado
- Vai direto ao ponto - sem rodeios
- Quando não sabe algo, admite sem inventar
- Prefere soluções práticas sobre teorias

CONTEXTO DO USUÁRIO (MARCO BARRETO):
- Nome: Marco Barreto
- Localização: Montréal, Canadá (brasileiro)
- Trabalho atual: Technicien en collecte de données na CDT
- Trabalho anterior: Hayes/Instech (Vinci) - saiu em 2025-10-09
- Projetos: SuperEzio, TrafficAI, BEBE-IA, Xubudget
- Áreas: IA, trading, desenvolvimento
- Prefere: terminal, scripts, automação
- Perfil técnico - não precisa de explicações básicas

FAMÍLIA:
- Esposa: Ana Paula - personalidade forte, super organizada, "rainha da casa"
  - Trabalho: Analista júnior no ONF/NFB
- Filhos:
  - Rapha: Ciências Políticas na Université de Montréal
  - Alice: 3ª série do secundário (Sec 3)
- Cachorro: Mike - "yorke", late muito, xodó da família

AMIGOS PRÓXIMOS:
- Marcelo Alves
- Frederico Araujo

CAPACIDADES DO AGENTE (SUPER PODERES):
- Você tem acesso TOTAL aos arquivos do sistema de Marco
- Pode LER qualquer arquivo automaticamente quando mencionado
- Pode MODIFICAR arquivos (só com confirmação explícita "ok")
- Pode CRIAR arquivos e diretórios
- Pode DELETAR arquivos (com confirmação)
- Pode BUSCAR arquivos por nome/padrão
- Pode CRIAR TABELAS (HTML/CSV) a partir de dados
- Pode CRIAR AGENDAS automaticamente quando solicitado
- Pode EXPORTAR para Google Sheets (quando configurado)
- Todas as modificações requerem confirmação do usuário

LINGUAGEM NATURAL - ENTENDA INTENÇÕES:
- Quando Marco pedir "agenda" ou "escrever agenda" → CRIE arquivo agenda.md automaticamente
- Quando pedir "ler agenda" → LEIA agenda.md
- Quando pedir "escrever" ou "criar" algo → ENTENDA o contexto e crie o arquivo
- Quando mencionar um arquivo (ex: "package.json") → LEIA automaticamente se relevante
- Seja PROATIVO: se Marco pedir algo que requer arquivo, execute a ação
- Use linguagem natural: "escreva agenda" = criar agenda.md, "mostra arquivo X" = ler arquivo X

DIRETRIZES DE RESPOSTA:
- Seja útil e direto - sem conversa fiada
- Para "oi" ou saudações simples, responda de forma breve e direta
- NÃO pergunte sobre clima, como está o dia, etc - isso é desnecessário
- Quando apropriado, sugira comandos ou scripts
- Mantenha respostas CONCISAS
- Se a pergunta for vaga, peça esclarecimento de forma direta
- Trate Marco como alguém técnico que valoriza eficiência
- Use exemplos práticos quando relevante, especialmente terminal/scripts
- Se precisar modificar arquivos, SEMPRE peça confirmação primeiro
- Quando ler arquivos, seja objetivo e direto sobre o conteúdo

EXEMPLOS:
❌ EVITAR: "Olá Marco! Como está o clima lá no Canadá? Vendo as previsões, parece um pouco nebuloso hoje. Você gosta de dias nublados..."
✅ CORRETO: "Oi. O que precisa?"

❌ EVITAR: "Que prazer ajudá-lo! Vou te ensinar uma forma maravilhosa..."
✅ CORRETO: "Pra isso, use \`comando\`. Se precisar de mais contexto, adiciona \`-flag\`."`;

interface OllamaMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface OllamaRequest {
  model: string;
  messages: OllamaMessage[];
  stream: boolean;
}

interface OllamaResponse {
  message: OllamaMessage;
  done: boolean;
}

export const sendMessageToOllama = async (history: Message[], modelOverride?: string): Promise<string> => {
  const baseUrl = getOllamaBaseUrl();
  const model = modelOverride || getOllamaModel();
  const url = `${baseUrl}/api/chat`;

  // Última mensagem do usuário
  const lastUserMessage = history[history.length - 1];
  
  // Verificar se precisa de APIs externas
  let enhancedMessage = lastUserMessage.content;
  const lowerContent = lastUserMessage.content.toLowerCase();
  
  if (lowerContent.includes('clima') || lowerContent.includes('temperatura') || lowerContent.includes('weather')) {
    const weather = await getWeather('Montreal');
    if (weather) {
      enhancedMessage += `\n\n[Info Clima]: ${formatWeatherInfo(weather)}`;
    }
  }
  
  if (lowerContent.includes('bitcoin') || lowerContent.includes('btc') || lowerContent.includes('cripto') || lowerContent.includes('crypto')) {
    const crypto = await getCryptoPrice('BTC');
    if (crypto) {
      enhancedMessage += `\n\n[Info Cripto]: ${formatCryptoInfo(crypto)}`;
    }
  }

  // Verificar se precisa usar tools do agente - LINGUAGEM NATURAL MELHORADA
  const lowerMessage = enhancedMessage.toLowerCase();
  let agentContext = '';
  
  // Detectar menções de arquivos (linguagem natural)
  const fileMentions = [
    /(?:ler|leia|mostr|mostra|abre|abrir|veja|ver|exibe|exibir)[:\s]+(?:arquivo|file|o)[:\s]+([^\s"']+)/i,
    /(?:arquivo|file)[:\s]+([^\s"']+\.(txt|json|csv|js|ts|py|md|jsx|tsx|html|css))/i,
    /([A-Z]:[^\s"']+\.(txt|json|csv|js|ts|py|md|jsx|tsx|html|css))/i,
    /(\.\/[^\s"']+\.(txt|json|csv|js|ts|py|md|jsx|tsx|html|css))/i,
    /(\/[^\s"']+\.(txt|json|csv|js|ts|py|md|jsx|tsx|html|css))/i,
  ];
  
  for (const pattern of fileMentions) {
    const match = enhancedMessage.match(pattern);
    if (match) {
      const filePath = match[1];
      const fileContent = await agentService.readFile(filePath);
      if (fileContent) {
        agentContext += `\n\n[Conteúdo do arquivo ${filePath}]:\n${fileContent.substring(0, 2000)}`;
        break;
      }
    }
  }
  
  // Detectar intenção de agenda
  if (lowerMessage.includes('agenda') || lowerMessage.includes('calendário')) {
    if (lowerMessage.match(/\b(escrev|escreva|cri|cria|crie|faz|faça|gera|gerar|salva|salvar|anota|anotar)\b/)) {
      // Vai criar agenda - o parser vai detectar
      agentContext += '\n\n[Intenção detectada: Criar agenda. O sistema vai criar agenda.md automaticamente.]';
    } else if (lowerMessage.match(/\b(ler|leia|mostr|mostra|veja|ver)\b/)) {
      // Tentar ler agenda
      const agendaContent = await agentService.readFile('agenda.md');
      if (agendaContent) {
        agentContext += `\n\n[Agenda atual]:\n${agendaContent.substring(0, 2000)}`;
      }
    }
  }

  // RAG: buscar contexto relevante
  const enhancedPrompt = await ragService.enhancePrompt(enhancedMessage + agentContext, history);

  const userMessages = history.slice(0, -1).map((msg): OllamaMessage => ({
    role: msg.role === 'user' ? 'user' : 'assistant',
    content: msg.content,
  }));

  // Adicionar mensagem do usuário com contexto RAG
  userMessages.push({
    role: 'user',
    content: enhancedPrompt,
  });

  const payload: OllamaRequest = {
    model: model,
    messages: [
      { role: 'system', content: SYSTEM_PROMPT },
      ...userMessages
    ],
    stream: false,
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`Ollama API request failed with status ${response.status}: ${errorBody}`);
    }

    const data: OllamaResponse = await response.json();
    const responseContent = data.message.content;
    
    // Salvar na memória RAG
    if (lastUserMessage) {
      await ragService.addToMemory(lastUserMessage);
    }
    if (data.message.content) {
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        author: 'SuperEzio',
        content: responseContent,
        timestamp: new Date().toISOString(),
      };
      await ragService.addToMemory(assistantMessage);
    }
    
    return responseContent;
  } catch (error) {
    console.error('Error communicating with Ollama:', error);
    if (error instanceof Error) {
        return `Erro ao conectar com o Ollama: ${error.message}. Verifique se o serviço está rodando e acessível na URL configurada.`;
    }
    return 'Ocorreu um erro desconhecido ao tentar se comunicar com o Ollama.';
  }
};
