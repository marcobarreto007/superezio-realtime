import { ToolExecution } from '../../server/agentTools';

const API_BASE = '/api/agent';

export interface AgentResponse {
  content?: string;
  tool_calls?: ToolCall[];
  error?: string;
}

export interface ToolCall {
  function: {
    name: string;
    arguments: string; // JSON string
  };
  id?: string;
  type?: 'function';
}

export const agentService = {
  /**
   * Lists all available tools.
   */
  async listTools() {
    const res = await fetch(`${API_BASE}/tools`);
    return res.json();
  },

  /**
   * Executes a tool.
   * @param toolName The name of the tool to execute.
   * @param parameters The parameters for the tool.
   * @param confirmed Whether the user has confirmed the execution (for dangerous tools).
   */
  async executeTool(toolName: string, parameters: Record<string, any>, confirmed: boolean = false): Promise<ToolExecution> {
    const res = await fetch(`${API_BASE}/tools/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ toolName, parameters, confirmed }),
    });
    return res.json();
  },

  /**
   * Reads a file directly (shortcut).
   */
  async readFile(path: string) {
    const res = await fetch(`${API_BASE}/files/read?path=${encodeURIComponent(path)}`);
    return res.json();
  },

  /**
   * Lists a directory (shortcut).
   */
  async listDirectory(path: string) {
    const res = await fetch(`${API_BASE}/files/list?path=${encodeURIComponent(path)}`);
    return res.json();
  }
};
