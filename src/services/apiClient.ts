import type { Message, ChatResponse } from '../types';

const API_BASE = '/api/hf';

export async function sendMessage(
  messages: Message[],
  options: { temperature?: number; maxTokens?: number; signal?: AbortSignal } = {}
): Promise<string> {
  const { temperature = 0.7, maxTokens = 512, signal } = options;

  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages,
      model: 'Qwen2.5-7B-Instruct',
      temperature,
      max_tokens: maxTokens,
    }),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Erro ${response.status}`);
  }

  const data: ChatResponse = await response.json();
  return data.content || 'Sem resposta';
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    const data = await response.json();
    return data.status === 'healthy';
  } catch {
    return false;
  }
}
