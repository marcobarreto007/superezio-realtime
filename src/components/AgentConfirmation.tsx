import React from 'react';
import { AlertTriangle, Check, X, FileCode, FolderOpen, Trash2, Mail } from 'lucide-react';
import { PendingAction } from '../hooks/useAgent';

interface AgentConfirmationProps {
  action: PendingAction;
  onConfirm: () => void;
  onCancel: () => void;
  isExecuting: boolean;
}

export const AgentConfirmation: React.FC<AgentConfirmationProps> = ({
  action,
  onConfirm,
  onCancel,
  isExecuting
}) => {
  const getIcon = () => {
    if (action.toolName.includes('delete')) return <Trash2 className="w-6 h-6 text-red-500" />;
    if (action.toolName.includes('write')) return <FileCode className="w-6 h-6 text-orange-500" />;
    if (action.toolName.includes('directory')) return <FolderOpen className="w-6 h-6 text-blue-500" />;
    return <AlertTriangle className="w-6 h-6 text-yellow-500" />;
  };

  const getDescription = () => {
    switch (action.toolName) {
      case 'write_file':
        return `Criar/Sobrescrever arquivo: ${action.parameters.path}`;
      case 'delete_file':
        return `DELETAR arquivo permanentemente: ${action.parameters.path}`;
      case 'create_directory':
        return `Criar pasta: ${action.parameters.path}`;
      default:
        return `Executar ação: ${action.toolName}`;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-gray-800 border border-gray-700 rounded-xl shadow-2xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in duration-200">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-gray-900/50 rounded-full border border-gray-700">
              {getIcon()}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Confirmação de Agente</h3>
              <p className="text-sm text-gray-400">O assistente solicita permissão</p>
            </div>
          </div>

          <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700/50 mb-6">
            <p className="text-gray-300 font-mono text-sm break-all">
              {getDescription()}
            </p>
            {action.parameters.content && (
              <div className="mt-3 pt-3 border-t border-gray-700/50">
                <p className="text-xs text-gray-500 mb-1">Conteúdo (preview):</p>
                <pre className="text-xs text-gray-400 font-mono bg-black/30 p-2 rounded overflow-x-auto max-h-32">
                  {action.parameters.content.substring(0, 200)}
                  {action.parameters.content.length > 200 && '...'}
                </pre>
              </div>
            )}
          </div>

          <div className="flex gap-3">
            <button
              onClick={onCancel}
              disabled={isExecuting}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors"
            >
              <X className="w-4 h-4" />
              Cancelar
            </button>
            <button
              onClick={onConfirm}
              disabled={isExecuting}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium transition-colors shadow-lg shadow-blue-500/20"
            >
              {isExecuting ? (
                <span className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full" />
              ) : (
                <Check className="w-4 h-4" />
              )}
              Confirmar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
