// Sistema de Tools/Funções para o Agente SuperEzio
// Permite que o agente execute ações no sistema

import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { readEmails, searchEmails, getUnreadCount } from './emailService.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Diretório raiz do projeto SuperEzio Realtime
const PROJECT_ROOT = path.resolve(__dirname, '..');

// Normalizar caminho para sempre ser relativo ao projeto
function normalizePath(filePath) {
  // Se for caminho absoluto, usar como está
  if (path.isAbsolute(filePath)) {
    return filePath;
  }
  
  // Se começar com ./, remover o ./
  if (filePath.startsWith('./')) {
    filePath = filePath.substring(2);
  }
  
  // Resolver relativo ao diretório do projeto
  return path.resolve(PROJECT_ROOT, filePath);
}

export const AVAILABLE_TOOLS = [
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
export async function executeTool(toolName, parameters = {}, confirmed = false) {
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
    let result;

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
        const listPath = normalizePath(parameters.dirPath);
        const items = await fs.readdir(listPath);
        const details = await Promise.all(
          items.map(async (item) => {
            const itemPath = path.join(listPath, item);
            const stats = await fs.stat(itemPath);
            return {
              name: item,
              type: stats.isDirectory() ? 'directory' : 'file',
              size: stats.size,
              modified: stats.mtime.toISOString(),
            };
          })
        );
        result = details;
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
        const stats = await fs.stat(infoPath);
        result = {
          path: infoPath,
          size: stats.size,
          created: stats.birthtime.toISOString(),
          modified: stats.mtime.toISOString(),
          isDirectory: stats.isDirectory(),
          isFile: stats.isFile(),
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
  } catch (error) {
    return {
      tool: toolName,
      parameters,
      error: error.message,
      timestamp: new Date().toISOString(),
    };
  }
}

// Buscar arquivos recursivamente
async function searchFilesRecursive(dirPath, pattern) {
  const results = [];
  const regex = new RegExp(pattern, 'i');
  const normalizedDir = normalizePath(dirPath);

  async function search(currentPath) {
    try {
      const items = await fs.readdir(currentPath);
      for (const item of items) {
        const itemPath = path.join(currentPath, item);
        const stats = await fs.stat(itemPath);
        
        if (stats.isDirectory()) {
          await search(itemPath);
        } else if (regex.test(item)) {
          // Retornar caminho relativo ao projeto
          const relativePath = path.relative(PROJECT_ROOT, itemPath);
          results.push(relativePath);
        }
      }
    } catch (error) {
      // Ignorar erros de permissão
    }
  }

  await search(normalizedDir);
  return results;
}

// Criar tabela
async function createTable(data, format, outputPath) {
  if (format === 'csv') {
    const headers = Object.keys(data[0] || {});
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
    const headers = Object.keys(data[0] || {});
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
