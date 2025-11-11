// Provider selector for browser (ESM). Avoids `require` (not available in browser).
// Both modules are statically imported; selection happens at runtime via env.

import { startChat as startOllama } from './ollamaService';
import { startChat as startGemini } from './geminiService';

const provider = ((process.env.MODEL_PROVIDER as string) || 'gemini').toLowerCase();

export const startChat = () => {
  return provider === 'ollama' ? startOllama() : startGemini();
};
