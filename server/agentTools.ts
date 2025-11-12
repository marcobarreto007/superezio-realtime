// Sistema de Tools/Funções para o Agente SuperEzio
// Permite que o agente execute ações no sistema

import fs from 'fs-extra';
import path from 'path';
import { readEmails, searchEmails, getUnreadCount } from './emailService.js'; // Usar .js na importação para compatibilidade com módulos ES

// Interfaces para tipagem
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
  message?: string;
}

// Diretório raiz do projeto SuperEzio Realtime
const PROJECT_ROOT = path.resolve(process.cwd());

// Normalizar caminho - VERSÃO ROBUSTA E HONESTA
function normalizePath(filePath: string): string {
  console.log(`[AgentTools] normalizePath INPUT: "${filePath}"`);
  
  if (path.isAbsolute(filePath) || filePath.match(/^[A-Z]:\\/i)) {
    console.log(`[AgentTools] Caminho absoluto detectado: ${filePath}`);
    return filePath;
  }
  
  // Para todos os outros casos (relativos, nome simples), resolve a partir do diretório de trabalho atual
  const resolved = path.resolve(process.cwd(), filePath);
  console.log(`[AgentTools] Caminho resolvido: ${filePath} -> ${resolved}`);
  return resolved;
}

export const AVAILABLE_TOOLS: AgentTool[] = [
  {
    name: 'read_file',
    description: 'Lê o conteúdo de um arquivo',
    parameters: { filePath: 'string' },
    requiresConfirmation: false,
  },
  {
    name: 'write_file',
    description: 'Escreve conteúdo em um arquivo (cria ou sobrescreve)',
    parameters: { filePath: 'string', content: 'string' },
    requiresConfirmation: true,
  },
  {
    name: 'list_directory',
    description: 'Lista arquivos e pastas em um diretório',
    parameters: { dirPath: 'string' },
    requiresConfirmation: false,
  },
  {
    name: 'create_directory',
    description: 'Cria um novo diretório',
    parameters: { dirPath: 'string' },
    requiresConfirmation: true,
  },
  {
    name: 'delete_file',
    description: 'Deleta um arquivo ou diretório',
    parameters: { filePath: 'string' },
    requiresConfirmation: true,
  },
  {
    name: 'search_files',
    description: 'Busca arquivos por nome ou padrão',
    parameters: { searchPath: 'string', pattern: 'string' },
    requiresConfirmation: false,
  },
  {
    name: 'get_file_info',
    description: 'Obtém informações sobre um arquivo (tamanho, data, etc)',
    parameters: { filePath: 'string' },
    requiresConfirmation: false,
  },
  {
    name: 'create_table',
    description: 'Cria uma tabela HTML/CSV a partir de dados',
    parameters: { data: 'array', format: 'string (html|csv)', outputPath: 'string' },
    requiresConfirmation: true,
  },
  {
    name: 'read_emails',
    description: 'Lê emails recentes da caixa de entrada',
    parameters: { limit: 'number (opcional, padrão: 10)', folder: 'string (opcional, padrão: INBOX)' },
    requiresConfirmation: false,
  },
  {
    name: 'search_emails',
    description: 'Busca emails por assunto ou remetente',
    parameters: { query: 'string', limit: 'number (opcional, padrão: 10)' },
    requiresConfirmation: false,
  },
  {
    name: 'get_unread_count',
    description: 'Obtém quantidade de emails não lidos',
    parameters: {},
    requiresConfirmation: false,
  },
];

// Executar uma tool
export async function executeTool(toolName: string, parameters: Record<string, any> = {}, confirmed: boolean = false): Promise<ToolExecution> {
  const tool = AVAILABLE_TOOLS.find(t => t.name === toolName);
  
  if (!tool) {
    return {
      tool: toolName,
      parameters,
      error: `Tool '${toolName}' não encontrada`,
      timestamp: new Date().toISOString(),
    };
  }

  if (tool.requiresConfirmation && !confirmed) {
    return {
      tool: toolName,
      parameters,
      error: 'Confirmação necessária para executar esta ação',
      timestamp: new Date().toISOString(),
    };
  }

  try {
    let result: any;

    switch (toolName) {
      case 'read_file':
        const readPath = normalizePath(parameters.filePath);
        result = await fs.readFile(readPath, 'utf-8');
        break;

      case 'write_file':
        const writePath = normalizePath(parameters.filePath);
        await fs.ensureDir(path.dirname(writePath));
        await fs.writeFile(writePath, parameters.content, 'utf-8');
        result = { success: true, message: `Arquivo escrito: ${writePath}` };
        break;

      case 'list_directory':
        try {
          const listPath = normalizePath(parameters.dirPath || '.');
          console.log(`[AgentTools] Tentando listar: ${listPath}`);
          
          if (!await fs.pathExists(listPath)) {
            throw new Error(`O diretório "${listPath}" NÃO EXISTE.`);
          }
          
          const stats = await fs.stat(listPath);
          if (!stats.isDirectory()) {
            throw new Error(`"${listPath}" existe mas NÃO É UM DIRETÓRIO.`);
          }
          
          const items = await fs.readdir(listPath);
          const details = await Promise.all(
            items.map(async (item) => {
              const itemPath = path.join(listPath, item);
              const itemStats = await fs.stat(itemPath);
              return {
                name: item,
                type: itemStats.isDirectory() ? 'directory' : 'file',
                size: itemStats.size,
                modified: itemStats.mtime.toISOString(),
              };
            })
          );
          
          result = {
            success: true,
            requestedPath: parameters.dirPath,
            resolvedPath: listPath,
            total: details.length,
            items: details.sort((a, b) => {
              if (a.type !== b.type) return a.type === 'directory' ? -1 : 1;
              return a.name.localeCompare(b.name);
            }),
          };
        } catch (error: any) {
          result = {
            error: `Erro ao acessar "${parameters.dirPath}": ${error.message}`,
            requestedPath: parameters.dirPath,
            resolvedPath: normalizePath(parameters.dirPath || '.'),
          };
        }
        break;

      case 'create_directory':
        const createPath = normalizePath(parameters.dirPath);
        await fs.ensureDir(createPath);
        result = { success: true, message: `Diretório criado: ${createPath}` };
        break;

      case 'delete_file':
        const deletePath = normalizePath(parameters.filePath);
        await fs.remove(deletePath);
        result = { success: true, message: `Arquivo deletado: ${deletePath}` };
        break;

      case 'search_files':
        const searchPath = normalizePath(parameters.searchPath);
        result = await searchFilesRecursive(searchPath, parameters.pattern);
        break;

      case 'get_file_info':
        const infoPath = normalizePath(parameters.filePath);
        const fileStats = await fs.stat(infoPath);
        result = {
          path: infoPath,
          size: fileStats.size,
          created: fileStats.birthtime.toISOString(),
          modified: fileStats.mtime.toISOString(),
          isDirectory: fileStats.isDirectory(),
          isFile: fileStats.isFile(),
        };
        break;

      case 'create_table':
        result = await createTable(parameters.data, parameters.format, parameters.outputPath);
        break;

      case 'read_emails':
        result = await readEmails(parameters.limit || 10, parameters.folder || 'INBOX');
        break;

      case 'search_emails':
        if (!parameters.query) {
          result = { error: 'Parâmetro "query" é obrigatório' };
        } else {
          result = await searchEmails(parameters.query, parameters.limit || 10);
        }
        break;

      case 'get_unread_count':
        result = { unreadCount: await getUnreadCount() };
        break;

      default:
        result = { error: `Tool '${toolName}' ainda não implementada` };
    }

    return {
      tool: toolName,
      parameters,
      result,
      timestamp: new Date().toISOString(),
    };
  } catch (error: any) {
    return {
      tool: toolName,
      parameters,
      error: error.message,
      timestamp: new Date().toISOString(),
    };
  }
}

async function searchFilesRecursive(dirPath: string, pattern: string): Promise<string[]> {
  const results: string[] = [];
  const regex = new RegExp(pattern, 'i');
  
  async function search(currentPath: string) {
    try {
      const items = await fs.readdir(currentPath);
      for (const item of items) {
        const itemPath = path.join(currentPath, item);
        const stats = await fs.stat(itemPath);
        
        if (stats.isDirectory()) {
          await search(itemPath);
        } else if (regex.test(item)) {
          results.push(path.relative(PROJECT_ROOT, itemPath));
        }
      }
    } catch (error) {
      // Ignorar erros de permissão
    }
  }

  await search(dirPath);
  return results;
}

async function createTable(data: any[], format: string, outputPath?: string): Promise<any> {
  if (!Array.isArray(data) || data.length === 0) {
    return { error: 'Dados de entrada inválidos ou vazios.' };
  }

  const headers = Object.keys(data[0]);
  
  if (format === 'csv') {
    const csv = [
      headers.join(','),
      ...data.map(row => headers.map(h => `"${String(row[h] || '').replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    if (outputPath) {
      await fs.writeFile(outputPath, csv, 'utf-8');
      return { success: true, message: `CSV criado: ${outputPath}`, preview: csv.substring(0, 500) };
    }
    return { csv, preview: csv.substring(0, 500) };
  }

  if (format === 'html') {
    const html = `
      <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead>
          <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
        </thead>
        <tbody>
          ${data.map(row => `<tr>${headers.map(h => `<td>${row[h] || ''}</td>`).join('')}</tr>`).join('')}
        </tbody>
      </table>
    `;

    if (outputPath) {
      await fs.writeFile(outputPath, html, 'utf-8');
      return { success: true, message: `HTML criado: ${outputPath}`, html };
    }
    return { html };
  }

  return { error: 'Formato não suportado. Use "csv" ou "html"' };
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}
