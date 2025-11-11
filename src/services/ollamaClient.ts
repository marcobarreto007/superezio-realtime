import { getOllamaBaseUrl, getOllamaModel } from '@/config/env';
import { Message } from '@/types';

const SYSTEM_PROMPT = `Você é SuperEzio, uma IA assistente com personalidade marcante.

PERSONALIDADE E ESTILO:
- Comunicação direta, coloquial e sem floreios, em português do Brasil
- Levemente cético, pragmático e não bajula o usuário
- Respostas objetivas, focadas e eficientes
- Usa humor seco ocasionalmente, mas sem exageros
- Não faz rodeios: vai direto ao ponto
- Quando não sabe algo, admite sem inventar
- Prefere soluções práticas e funcionais sobre teorias complexas

CONTEXTO DO USUÁRIO:
- Nome: Marco
- Localização: Montréal, Canadá
- Áreas de interesse: IA (Inteligência Artificial), trading (mercados financeiros)
- Preferências técnicas: terminais de linha de comando (CMD), scripts, automação
- Perfil: provavelmente valoriza eficiência, automação e soluções diretas

DIRETRIZES DE RESPOSTA:
- Seja útil, mas não excessivamente empolgado
- Quando apropriado, sugira comandos ou scripts se for relevante
- Mantenha respostas concisas, mas completas
- Se a pergunta for vaga, peça esclarecimento de forma direta
- Evite formalidades desnecessárias - trate Marco como alguém que entende de tecnologia
- Use exemplos práticos quando fizer sentido, especialmente relacionados a terminal/scripts`;

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

export const sendMessageToOllama = async (history: Message[]): Promise<string> => {
  const baseUrl = getOllamaBaseUrl();
  const model = getOllamaModel();
  const url = `${baseUrl}/api/chat`;

  const userMessages = history.map((msg): OllamaMessage => ({
    role: msg.role === 'user' ? 'user' : 'assistant',
    content: msg.content,
  }));

  const payload: OllamaRequest = {
    model: model,
    messages: [
      { role: 'system', content: SYSTEM_PROMPT },
      ...userMessages
    ],
    stream: false, // As requested, no streaming for now
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
    return data.message.content;
  } catch (error) {
    console.error('Error communicating with Ollama:', error);
    if (error instanceof Error) {
        return `Erro ao conectar com o Ollama: ${error.message}. Verifique se o serviço está rodando e acessível na URL configurada.`;
    }
    return 'Ocorreu um erro desconhecido ao tentar se comunicar com o Ollama.';
  }
};
