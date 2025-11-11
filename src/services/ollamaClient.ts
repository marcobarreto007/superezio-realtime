import { getOllamaBaseUrl, getOllamaModel } from '@/config/env';
import { Message } from '@/types';
import { ragService } from './ragService';
import { getWeather, getCryptoPrice, formatWeatherInfo, formatCryptoInfo } from './externalAPIs';

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

DIRETRIZES DE RESPOSTA:
- Seja útil e direto - sem conversa fiada
- Para "oi" ou saudações simples, responda de forma breve e direta
- NÃO pergunte sobre clima, como está o dia, etc - isso é desnecessário
- Quando apropriado, sugira comandos ou scripts
- Mantenha respostas CONCISAS
- Se a pergunta for vaga, peça esclarecimento de forma direta
- Trate Marco como alguém técnico que valoriza eficiência
- Use exemplos práticos quando relevante, especialmente terminal/scripts

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

  // RAG: buscar contexto relevante
  const enhancedPrompt = await ragService.enhancePrompt(enhancedMessage, history);

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
