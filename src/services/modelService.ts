// Serviço para gerenciar modelos disponíveis

export interface ModelInfo {
  name: string;
  displayName: string;
  description: string;
}

export const availableModels: ModelInfo[] = [
  {
    name: 'qwen2.5:7b-instruct',
    displayName: 'Qwen 2.5 7B',
    description: 'Rápido e eficiente',
  },
  {
    name: 'llama3.1:8b',
    displayName: 'Llama 3.1 8B',
    description: 'Bom equilíbrio',
  },
  {
    name: 'gemma2:9b',
    displayName: 'Gemma 2 9B',
    description: 'Qualidade alta',
  },
  {
    name: 'phi3:mini',
    displayName: 'Phi-3 Mini',
    description: 'Leve e rápido',
  },
  {
    name: 'llama3:latest',
    displayName: 'Llama 3',
    description: 'Versão estável',
  },
  {
    name: 'deepseek-r1:7b',
    displayName: 'DeepSeek R1',
    description: 'Raciocínio',
  },
];

export const getModelDisplayName = (modelName: string): string => {
  const model = availableModels.find(m => m.name === modelName);
  return model ? model.displayName : modelName;
};

