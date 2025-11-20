// Sistema de Tools/Funções para o Agente SuperEzio
// Permite que o agente execute ações no sistema

import fs from 'fs-extra';
import path from 'path';
import os from 'os';
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
  
  if (!filePath) {
    return PROJECT_ROOT;
  }

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
    parameters: { path: 'string' },
    requiresConfirmation: false,
  },
  {
    name: 'write_file',
    description: 'Escreve conteúdo em um arquivo (cria ou sobrescreve)',
    parameters: { path: 'string', content: 'string' },
    requiresConfirmation: true,
  },
  {
    name: 'list_directory',
    description: 'Lista arquivos e pastas em um diretório',
    parameters: { path: 'string' },
    requiresConfirmation: false,
  },
  {
    name: 'create_directory',
    description: 'Cria um novo diretório',
    parameters: { path: 'string' },
    requiresConfirmation: true,
  },
  {
    name: 'delete_file',
    description: 'Deleta um arquivo ou diretório',
    parameters: { path: 'string' },
    requiresConfirmation: true,
  },
  {
    name: 'search_files',
    description: 'Busca arquivos por nome ou padrão',
    parameters: { path: 'string', pattern: 'string' },
    requiresConfirmation: false,
  },
  {
    name: 'get_file_info',
    description: 'Obtém informações sobre um arquivo (tamanho, data, etc)',
    parameters: { path: 'string' },
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
  {
    name: 'get_weather',
    description: 'Busca informações de clima/tempo para uma localidade e data. OBRIGATÓRIO usar antes de responder perguntas sobre clima. Se não houver API configurada, retorna erro indicando ausência de acesso a dados de clima em tempo real.',
    parameters: { location: 'string', date: 'string (opcional, padrão: hoje)' },
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
      requiresConfirmation: true, // Explicit flag
      message: `Confirmação necessária para executar: ${toolName}`,
      timestamp: new Date().toISOString(),
    };
  }

  try {
    let result: any;

    // Mapeamento de parâmetros antigos para novos (retrocompatibilidade)
    // Isso garante que parameters.path, parameters.filePath, etc sejam unificados
    const targetPath = parameters.path || parameters.filePath || parameters.dirPath || parameters.searchPath;

    switch (toolName) {
      case 'read_file':
        const readPath = normalizePath(targetPath);
        result = await fs.readFile(readPath, 'utf-8');
        break;

      case 'write_file':
        const writePath = normalizePath(targetPath);
        await fs.ensureDir(path.dirname(writePath));
        await fs.writeFile(writePath, parameters.content, 'utf-8');
        result = { success: true, message: `Arquivo escrito: ${writePath}` };
        break;

      case 'list_directory':
        try {
          const listPath = normalizePath(targetPath || '.');
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
            requestedPath: targetPath,
            resolvedPath: listPath,
            total: details.length,
            items: details.sort((a, b) => {
              if (a.type !== b.type) return a.type === 'directory' ? -1 : 1;
              return a.name.localeCompare(b.name);
            }),
          };
        } catch (error: any) {
          result = {
            error: `Erro ao acessar "${targetPath}": ${error.message}`,
            requestedPath: targetPath,
            resolvedPath: normalizePath(targetPath || '.'),
          };
        }
        break;

      case 'create_directory':
        const createPath = normalizePath(targetPath);
        await fs.ensureDir(createPath);
        result = { success: true, message: `Diretório criado: ${createPath}` };
        break;

      case 'delete_file':
        const deletePath = normalizePath(targetPath);
        await fs.remove(deletePath);
        result = { success: true, message: `Arquivo deletado: ${deletePath}` };
        break;

      case 'search_files':
        // Resolver Desktop do usuário se mencionado - Lógica da branch MAIN integrada
        let searchPathToUse = targetPath; // Usa targetPath unificado

        if (searchPathToUse && (searchPathToUse.toLowerCase().includes('desktop') || !path.isAbsolute(searchPathToUse))) {
          const userHome = os.homedir();
          if (searchPathToUse.toLowerCase().includes('desktop')) {
            // Se menciona desktop explicitamente, tenta montar o caminho
            // Remove 'desktop' duplicado e barras iniciais
            const cleanSub = searchPathToUse.replace(/desktop/gi, '').replace(/^[\/\\]+/, '');
            searchPathToUse = path.join(userHome, 'Desktop', cleanSub);
          } else {
            // Caminho relativo - resolver a partir do Desktop por padrão (comportamento da MAIN)
            // Nota: normalizePath usa process.cwd(), mas aqui forçamos Desktop se for relativo para busca
            searchPathToUse = path.join(userHome, 'Desktop', searchPathToUse);
          }
        }

        // Se ainda não definido, usa o padrão normalizado
        const finalSearchPath = normalizePath(searchPathToUse || targetPath);
        result = await searchFilesRecursive(finalSearchPath, parameters.pattern);
        break;

      case 'get_file_info':
        const infoPath = normalizePath(targetPath);
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
        // Handle both formats (simple data array vs headers/rows)
        if (parameters.headers && parameters.rows) {
            // Convert to simple array of objects for internal createTable
            const data = parameters.rows.map((row: string[]) => {
                const obj: any = {};
                parameters.headers.forEach((header: string, i: number) => {
                    obj[header] = row[i];
                });
                return obj;
            });
            result = await createTable(data, parameters.format || 'csv', parameters.outputPath);
        } else {
            result = await createTable(parameters.data, parameters.format, parameters.outputPath);
        }
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

      case 'get_weather':
        // Verificar se há API key configurada
        const weatherApiKey = process.env.OPENWEATHER_API_KEY;

        if (!weatherApiKey) {
          result = {
            error: 'no_weather_api_configured',
            message: 'API de clima não está configurada. Não tenho acesso a dados de clima em tempo real.',
            location: parameters.location || 'não especificada',
            date: parameters.date || 'hoje',
          };
        } else {
          try {
            // Tentar buscar via OpenWeatherMap (ou outra API)
            const location = parameters.location || '';
            const date = parameters.date || 'today';

            // Por enquanto, retornar erro controlado até implementar a API real
            // TODO: Implementar chamada real à API de clima quando necessário
            result = {
              error: 'no_weather_api_configured',
              message: 'API de clima não está totalmente implementada ainda. Não tenho acesso a dados de clima em tempo real.',
              location: location,
              date: date,
            };
          } catch (error: any) {
            result = {
              error: 'weather_api_error',
              message: `Erro ao buscar clima: ${error.message}`,
              location: parameters.location || 'não especificada',
            };
          }
        }
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
  const regex = new RegExp(pattern.replace(/\*/g, '.*'), 'i'); // Basic glob to regex
  
  async function search(currentPath: string) {
    try {
      const items = await fs.readdir(currentPath);
      for (const item of items) {
        const itemPath = path.join(currentPath, item);
        const stats = await fs.stat(itemPath);
        
        if (stats.isDirectory()) {
          // Avoid infinite loops and massive scans (node_modules, .git)
          if (!itemPath.includes('node_modules') && !itemPath.includes('.git')) {
             await search(itemPath);
          }
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
        const writePath = normalizePath(outputPath);
        await fs.writeFile(writePath, csv, 'utf-8');
        return { success: true, message: `CSV criado: ${writePath}`, preview: csv.substring(0, 500) };
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
        const writePath = normalizePath(outputPath);
        await fs.writeFile(writePath, html, 'utf-8');
        return { success: true, message: `HTML criado: ${writePath}`, html };
    }
    return { html };
  }

  return { error: 'Formato não suportado. Use "csv" ou "html"' };
}
