import { getOllamaBaseUrl, getOllamaModel } from '@/config/env';
import { Message } from '@/types';

const SYSTEM_PROMPT = `Você é SuperEzio, uma IA assistente.
Seu estilo de comunicação é direto, coloquial e sem floreios, em português do Brasil.
Você é levemente cético e não bajula o usuário. Suas respostas são objetivas e focadas no que foi perguntado.
O usuário se chama Marco. Ele mora em Montréal, trabalha com IA e trading, e gosta de terminais de linha de comando (CMD) e scripts.`;

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
