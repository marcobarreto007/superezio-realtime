// Sistema de Tools/Funções para o Agente SuperEzio
// Permite que o agente execute ações no sistema

import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
        result = await fs.readFile(parameters.filePath, 'utf-8');
        break;

      case 'write_file':
        await fs.ensureDir(path.dirname(parameters.filePath));
        await fs.writeFile(parameters.filePath, parameters.content, 'utf-8');
        result = { success: true, message: `Arquivo escrito: ${parameters.filePath}` };
        break;

      case 'list_directory':
        const items = await fs.readdir(parameters.dirPath);
        const details = await Promise.all(
          items.map(async (item) => {
            const itemPath = path.join(parameters.dirPath, item);
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
        await fs.ensureDir(parameters.dirPath);
        result = { success: true, message: `Diretório criado: ${parameters.dirPath}` };
        break;

      case 'delete_file':
        await fs.remove(parameters.filePath);
        result = { success: true, message: `Arquivo deletado: ${parameters.filePath}` };
        break;

      case 'search_files':
        result = await searchFilesRecursive(parameters.searchPath, parameters.pattern);
        break;

      case 'get_file_info':
        const stats = await fs.stat(parameters.filePath);
        result = {
          path: parameters.filePath,
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

  async function search(currentPath) {
    try {
      const items = await fs.readdir(currentPath);
      for (const item of items) {
        const itemPath = path.join(currentPath, item);
        const stats = await fs.stat(itemPath);
        
        if (stats.isDirectory()) {
          await search(itemPath);
        } else if (regex.test(item)) {
          results.push(itemPath);
        }
      }
    } catch (error) {
      // Ignorar erros de permissão
    }
  }

  await search(dirPath);
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
