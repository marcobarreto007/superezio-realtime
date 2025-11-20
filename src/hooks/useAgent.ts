import { useState, useCallback } from 'react';
import { agentService, ToolCall } from '../services/agentService';
import { ToolExecution } from '../../server/agentTools';

export interface PendingAction {
  toolName: string;
  parameters: Record<string, any>;
  id: string;
}

export function useAgent() {
  const [pendingAction, setPendingAction] = useState<PendingAction | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [lastResult, setLastResult] = useState<ToolExecution | null>(null);

  /**
   * Processes tool calls from the LLM.
   * If a tool requires confirmation, it sets the pending action.
   * Otherwise, it executes immediately.
   */
  const processToolCalls = useCallback(async (toolCalls: ToolCall[]) => {
    const results: ToolExecution[] = [];

    for (const call of toolCalls) {
      try {
        const toolName = call.function.name;
        let parameters = {};
        try {
          parameters = JSON.parse(call.function.arguments);
        } catch (e) {
          console.error("Failed to parse tool arguments:", call.function.arguments);
        }

        console.log(`[UseAgent] Processing tool: ${toolName}`, parameters);

        // First try to execute without confirmation flag
        // The backend will return { requiresConfirmation: true } if needed
        setIsExecuting(true);
        const initialResponse = await agentService.executeTool(toolName, parameters, false);
        setIsExecuting(false);

        if (initialResponse.requiresConfirmation) {
          console.log(`[UseAgent] Confirmation required for ${toolName}`);
          setPendingAction({
            toolName,
            parameters,
            id: call.id || Date.now().toString()
          });
          // Stop processing other tools until this one is resolved?
          // For simplicity, we pause here. In a complex agent, might queue them.
          return results;
        } else {
          results.push(initialResponse);
          setLastResult(initialResponse);
        }

      } catch (err: any) {
        console.error(`[UseAgent] Error executing ${call.function.name}:`, err);
        results.push({
          tool: call.function.name,
          parameters: {},
          error: err.message,
          timestamp: new Date().toISOString()
        });
      }
    }
    return results;
  }, []);

  /**
   * Confirms and executes the pending action.
   */
  const confirmAction = useCallback(async () => {
    if (!pendingAction) return;

    setIsExecuting(true);
    try {
      const result = await agentService.executeTool(
        pendingAction.toolName,
        pendingAction.parameters,
        true // Confirmed!
      );
      setLastResult(result);
      setPendingAction(null);
      return result;
    } catch (err) {
      console.error("Error confirming action:", err);
    } finally {
      setIsExecuting(false);
    }
  }, [pendingAction]);

  /**
   * Cancels the pending action.
   */
  const cancelAction = useCallback(() => {
    setPendingAction(null);
  }, []);

  return {
    pendingAction,
    isExecuting,
    lastResult,
    processToolCalls,
    confirmAction,
    cancelAction
  };
}
