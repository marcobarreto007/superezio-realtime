// Hook para gerenciar ações do agente
import { useState, useCallback } from 'react';
import { agentService, ToolExecution } from '@/services/agentService';
import { parseAgentCommand, ParsedCommand } from '@/services/agentCommandParser';

export const useAgent = () => {
  const [pendingAction, setPendingAction] = useState<ParsedCommand | null>(null);
  const [lastExecution, setLastExecution] = useState<ToolExecution | null>(null);

  const detectAndPrepareAction = useCallback((message: string): ParsedCommand | null => {
    const command = parseAgentCommand(message);
    if (command && command.detected) {
      setPendingAction(command);
      return command;
    }
    return null;
  }, []);

  const executeAction = useCallback(async (confirmed: boolean = false): Promise<ToolExecution | null> => {
    if (!pendingAction) return null;

    const result = await agentService.executeTool(
      pendingAction.tool,
      pendingAction.parameters,
      confirmed
    );

    setLastExecution(result);
    
    if (!result.error || !result.requiresConfirmation) {
      setPendingAction(null);
    }

    return result;
  }, [pendingAction]);

  const cancelAction = useCallback(() => {
    setPendingAction(null);
  }, []);

  return {
    pendingAction,
    lastExecution,
    detectAndPrepareAction,
    executeAction,
    cancelAction,
  };
};

