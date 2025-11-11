// Parser de comandos do agente
// Detecta quando o SuperEzio quer executar uma ação e extrai parâmetros

import { agentService } from './agentService';

export interface ParsedCommand {
  tool: string;
  parameters: Record<string, any>;
  requiresConfirmation: boolean;
  detected: boolean;
}

export const parseAgentCommand = (message: string): ParsedCommand | null => {
  const lower = message.toLowerCase();
  
  // Padrões de detecção
  const patterns = [
    {
      tool: 'read_file',
      triggers: ['ler arquivo', 'read file', 'abrir arquivo', 'mostrar arquivo', 'conteúdo do arquivo'],
      extractPath: (msg: string) => {
        const match = msg.match(/(?:arquivo|file)[:\s]+([^\s"']+)/i) || 
                     msg.match(/([A-Z]:[^\s"']+)/) ||
                     msg.match(/(\.\/[^\s"']+)/) ||
                     msg.match(/(\/[^\s"']+)/);
        return match ? match[1] : null;
      },
    },
    {
      tool: 'write_file',
      triggers: ['escrever arquivo', 'criar arquivo', 'salvar arquivo', 'write file', 'create file'],
      extractPath: (msg: string) => {
        const match = msg.match(/(?:arquivo|file)[:\s]+([^\s"']+)/i) || 
                     msg.match(/(?:em|to|para)[:\s]+([^\s"']+)/i);
        return match ? match[1] : null;
      },
      extractContent: (msg: string) => {
        // Tentar extrair conteúdo entre aspas ou após "com conteúdo"
        const contentMatch = msg.match(/com conteúdo[:\s]+"([^"]+)"/i) ||
                            msg.match(/content[:\s]+"([^"]+)"/i) ||
                            msg.match(/"([^"]+)"/);
        return contentMatch ? contentMatch[1] : null;
      },
    },
    {
      tool: 'list_directory',
      triggers: ['listar pasta', 'listar diretório', 'list directory', 'mostrar pasta', 'arquivos em'],
      extractPath: (msg: string) => {
        const match = msg.match(/(?:pasta|diretorio|directory|folder)[:\s]+([^\s"']+)/i) ||
                     msg.match(/(?:em|in)[:\s]+([^\s"']+)/i);
        return match ? match[1] : null;
      },
    },
    {
      tool: 'search_files',
      triggers: ['buscar arquivo', 'procurar arquivo', 'search file', 'find file'],
      extractPath: (msg: string) => {
        const match = msg.match(/(?:em|in)[:\s]+([^\s"']+)/i);
        return match ? match[1] : '.';
      },
      extractPattern: (msg: string) => {
        const match = msg.match(/(?:arquivo|file|nome)[:\s]+([^\s"']+)/i) ||
                     msg.match(/(?:chamado|called|named)[:\s]+([^\s"']+)/i);
        return match ? match[1] : '.*';
      },
    },
    {
      tool: 'create_table',
      triggers: ['criar tabela', 'gerar tabela', 'create table', 'tabela com'],
      extractData: (msg: string) => {
        // Tentar extrair dados JSON ou estrutura
        const jsonMatch = msg.match(/\[[\s\S]*\]/);
        if (jsonMatch) {
          try {
            return JSON.parse(jsonMatch[0]);
          } catch {}
        }
        return null;
      },
      extractFormat: (msg: string) => {
        if (lower.includes('csv')) return 'csv';
        if (lower.includes('html')) return 'html';
        return 'html'; // default
      },
    },
  ];

  for (const pattern of patterns) {
    for (const trigger of pattern.triggers) {
      if (lower.includes(trigger)) {
        const parameters: Record<string, any> = {};
        
        // Extrair parâmetros específicos
        if (pattern.extractPath) {
          const path = pattern.extractPath(message);
          if (path) {
            if (pattern.tool === 'read_file' || pattern.tool === 'write_file') {
              parameters.filePath = path;
            } else if (pattern.tool === 'list_directory') {
              parameters.dirPath = path;
            } else if (pattern.tool === 'search_files') {
              parameters.searchPath = path;
            }
          }
        }

        if (pattern.extractContent && pattern.tool === 'write_file') {
          const content = pattern.extractContent(message);
          if (content) parameters.content = content;
        }

        if (pattern.extractPattern && pattern.tool === 'search_files') {
          const patternValue = pattern.extractPattern(message);
          if (patternValue) parameters.pattern = patternValue;
        }

        if (pattern.extractData && pattern.tool === 'create_table') {
          const data = pattern.extractData(message);
          if (data) parameters.data = data;
          parameters.format = pattern.extractFormat ? pattern.extractFormat(message) : 'html';
        }

        return {
          tool: pattern.tool,
          parameters,
          requiresConfirmation: ['write_file', 'delete_file', 'create_directory', 'create_table'].includes(pattern.tool),
          detected: true,
        };
      }
    }
  }

  return null;
};

