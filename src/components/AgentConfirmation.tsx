// Componente para confirmar ações do agente
import React from 'react';

interface AgentConfirmationProps {
  tool: string;
  parameters: Record<string, any>;
  onConfirm: () => void;
  onCancel: () => void;
}

const AgentConfirmation: React.FC<AgentConfirmationProps> = ({
  tool,
  parameters,
  onConfirm,
  onCancel,
}) => {
  const getActionDescription = () => {
    switch (tool) {
      case 'write_file':
        return `Escrever arquivo: ${parameters.filePath}`;
      case 'delete_file':
        return `Deletar: ${parameters.filePath}`;
      case 'create_directory':
        return `Criar diretório: ${parameters.dirPath}`;
      case 'create_table':
        return `Criar tabela ${parameters.format}${parameters.outputPath ? ` em ${parameters.outputPath}` : ''}`;
      default:
        return `Executar: ${tool}`;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 border border-cyan-500/30">
        <h3 className="text-xl font-bold text-cyan-400 mb-4">Confirmação Necessária</h3>
        <p className="text-gray-300 mb-4">{getActionDescription()}</p>
        
        {tool === 'write_file' && parameters.content && (
          <div className="bg-gray-900 rounded p-3 mb-4 max-h-40 overflow-y-auto">
            <pre className="text-xs text-gray-400 whitespace-pre-wrap">
              {parameters.content.substring(0, 500)}
              {parameters.content.length > 500 ? '...' : ''}
            </pre>
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={onConfirm}
            className="flex-1 bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Confirmar (OK)
          </button>
          <button
            onClick={onCancel}
            className="flex-1 bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export default AgentConfirmation;

