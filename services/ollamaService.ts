// Lightweight adapter to mimic the Gemini Chat interface using Ollama's HTTP API
// It exposes startChat() returning an object with sendMessageStream({ message })

export type OllamaChatLike = {
  sendMessageStream: (args: { message: string }) => AsyncGenerator<{ text: string }, void, unknown>;
};

// Use Vite dev proxy in dev or PHP proxy in prod
const OLLAMA_BASE_URL = (process.env.OLLAMA_BASE_URL as string) || '/ollama';
const OLLAMA_MODEL = (process.env.OLLAMA_MODEL as string) || 'qwen2.5:7b-instruct';
const OLLAMA_ADAPTER = (process.env.OLLAMA_ADAPTER as string) || '';

const systemInstruction = `
You are Superezio, an advanced real-time financial assistant.
Your expertise lies in personal finance, investment strategies, and expense management.
Your tone is professional, insightful, and data-driven. You provide clear, actionable advice to help the user achieve their financial goals.
Start the conversation by introducing yourself as Superezio and asking what financial topic the user wishes to discuss.
When asked to generate a report (e.g., 'gere um relatorio'), format the data as CSV, clearly indicating the start and end of the CSV block with \`\`\`csv and \`\`\`.
Do not add any text before or after the CSV block in your response if a report is requested.
Communicate in the user's language, which appears to be Brazilian Portuguese.
`;

function buildMessages(userMessage: string) {
  const messages = [
    { role: 'system', content: systemInstruction },
  ] as Array<{ role: 'system' | 'user' | 'assistant'; content: string }>;

  if (userMessage !== undefined && userMessage !== null) {
    messages.push({ role: 'user', content: userMessage });
  }
  return messages;
}

async function* streamFromOllama(prompt: string) {
  const base = OLLAMA_BASE_URL.trim();
  const url = base.endsWith('.php') ? `${base}?path=/api/chat` : `${base}/api/chat`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: OLLAMA_MODEL,
      messages: buildMessages(prompt),
      stream: true,
      options: OLLAMA_ADAPTER ? { adapter: OLLAMA_ADAPTER } : undefined,
    }),
  });

  if (!res.ok || !res.body) {
    throw new Error(`Ollama request failed: ${res.status} ${res.statusText}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffered = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffered += decoder.decode(value, { stream: true });

    // Ollama streams JSON objects delimited by newlines
    const lines = buffered.split('\n');
    buffered = lines.pop() || '';
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const obj = JSON.parse(line);
        if (obj?.message?.content) {
          yield { text: obj.message.content as string };
        }
      } catch {
        // ignore malformed partials
      }
    }
  }
}

export const startChat = (): OllamaChatLike => {
  return {
    sendMessageStream: ({ message }: { message: string }) => streamFromOllama(message),
  };
};
