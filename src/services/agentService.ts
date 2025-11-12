// Serviço para comunicação com o Agente SuperEzio
// Permite que o SuperEzio execute ações no sistema

const AGENT_API_BASE = '/api/agent';

export interface AgentTool {
  name: string;
  description: string;
  parameters: Record<string, string>;
  requiresConfirmation: boolean;
}

export interface ToolExecution {
  tool: string;
  parameters: Record<string, any>;
  result?: any;
  error?: string;
  timestamp: string;
  requiresConfirmation?: boolean;
}

export const agentService = {
  // Listar tools disponíveis
  async getAvailableTools(): Promise<AgentTool[]> {
    try {
      const response = await fetch(`${AGENT_API_BASE}/tools`);
      const data = await response.json();
      return data.tools || [];
    } catch (error) {
      console.error('Error fetching tools:', error);
      return [];
    }
  },

  // Executar uma tool
  async executeTool(
    toolName: string,
    parameters: Record<string, any>,
    confirmed: boolean = false
  ): Promise<ToolExecution> {
    try {
      const response = await fetch(`${AGENT_API_BASE}/tools/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          toolName,
          parameters,
          confirmed,
        }),
      });

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Error executing tool:', error);
      return {
        tool: toolName,
        parameters,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
        timestamp: new Date().toISOString(),
      };
    }
  },

  // Ler arquivo
  async readFile(filePath: string): Promise<string | null> {
    try {
      const response = await fetch(`${AGENT_API_BASE}/files/read?path=${encodeURIComponent(filePath)}`);
      const data = await response.json();
      return data.result || null;
    } catch (error) {
      console.error('Error reading file:', error);
      return null;
    }
  },

  // Listar diretório
  async listDirectory(dirPath: string): Promise<any> {
    try {
      const response = await fetch(`${AGENT_API_BASE}/files/list?path=${encodeURIComponent(dirPath)}`);
      const data = await response.json();
      // Retornar o resultado completo (pode ser objeto ou array)
      return data.result || null;
    } catch (error) {
      console.error('Error listing directory:', error);
      return null;
    }
  },

  // Buscar arquivos
  async searchFiles(searchPath: string, pattern: string): Promise<string[]> {
    try {
      const response = await fetch(
        `${AGENT_API_BASE}/files/search?path=${encodeURIComponent(searchPath)}&pattern=${encodeURIComponent(pattern)}`
      );
      const data = await response.json();
      return data.result || [];
    } catch (error) {
      console.error('Error searching files:', error);
      return [];
    }
  },

  // Ler emails
  async readEmails(limit: number = 10, folder: string = 'INBOX'): Promise<any[]> {
    try {
      const response = await fetch(
        `${AGENT_API_BASE}/emails/read?limit=${limit}&folder=${encodeURIComponent(folder)}`
      );
      const data = await response.json();
      return data.result || [];
    } catch (error) {
      console.error('Error reading emails:', error);
      return [];
    }
  },

  // Buscar emails
  async searchEmails(query: string, limit: number = 10): Promise<any[]> {
    try {
      const response = await fetch(
        `${AGENT_API_BASE}/emails/search?query=${encodeURIComponent(query)}&limit=${limit}`
      );
      const data = await response.json();
      return data.result || [];
    } catch (error) {
      console.error('Error searching emails:', error);
      return [];
    }
  },

  // Contar emails não lidos
  async getUnreadCount(): Promise<number> {
    try {
      const response = await fetch(`${AGENT_API_BASE}/emails/unread`);
      const data = await response.json();
      return data.result?.unreadCount || 0;
    } catch (error) {
      console.error('Error getting unread count:', error);
      return 0;
    }
  },
};

