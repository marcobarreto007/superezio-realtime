export const getOllamaBaseUrl = (): string => {
  const baseUrl = import.meta.env.VITE_OLLAMA_BASE_URL;
  if (!baseUrl) {
    console.warn('VITE_OLLAMA_BASE_URL is not set. Defaulting to http://localhost:11434');
    return 'http://localhost:11434';
  }
  return baseUrl;
};

export const getOllamaModel = (): string => {
    const model = import.meta.env.VITE_OLLAMA_MODEL;
    if (!model) {
        console.warn('VITE_OLLAMA_MODEL is not set. Defaulting to llama3:8b');
        return 'llama3:8b';
    }
    return model;
}
