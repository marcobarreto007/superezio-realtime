// Parser de comandos do agente
// Detecta quando o SuperEzio quer executar uma ação e extrai parâmetros

import { agentService } from './agentService';

export interface ParsedCommand {
  tool: string;
  parameters: Record<string, any>;
  requiresConfirmation: boolean;
  detected: boolean;
}

// Detectar intenções em linguagem natural
const detectIntent = (message: string): { intent: string; confidence: number } | null => {
  const lower = message.toLowerCase();
  
  // Intenções de escrita/criação
  if (lower.match(/\b(escrev|escreva|cri|cria|crie|faça|faz|gera|gerar|salva|salvar|anota|anotar)\b/)) {
    if (lower.includes('agenda') || lower.includes('calendário') || lower.includes('calendar')) {
      return { intent: 'create_agenda', confidence: 0.9 };
    }
    if (lower.match(/\b(arquivo|file|documento|doc)\b/)) {
      return { intent: 'write_file', confidence: 0.8 };
    }
    return { intent: 'write', confidence: 0.7 };
  }
  
  // Intenções de leitura
  if (lower.match(/\b(ler|leia|mostr|mostra|abre|abrir|veja|ver|exibe|exibir)\b/)) {
    if (lower.match(/\b(arquivo|file|documento)\b/)) {
      return { intent: 'read_file', confidence: 0.8 };
    }
    if (lower.match(/\b(pasta|diretorio|directory|folder)\b/)) {
      return { intent: 'list_directory', confidence: 0.8 };
    }
  }
  
  // Intenções de busca
  if (lower.match(/\b(busc|procure|procura|encontr|find|search)\b/)) {
    if (lower.includes('email') || lower.includes('e-mail') || lower.includes('correio')) {
      return { intent: 'search_emails', confidence: 0.8 };
    }
    return { intent: 'search_files', confidence: 0.7 };
  }
  
  // Intenções de email
  if (lower.includes('email') || lower.includes('e-mail') || lower.includes('correio') || lower.includes('mensagem')) {
    if (lower.match(/\b(ler|leia|mostr|mostra|veja|ver|exibe|exibir|listar|lista)\b/)) {
      return { intent: 'read_emails', confidence: 0.9 };
    }
    if (lower.match(/\b(busc|procure|procura|encontr|find|search)\b/)) {
      return { intent: 'search_emails', confidence: 0.9 };
    }
    if (lower.match(/\b(não lido|unread|novo|novos)\b/)) {
      return { intent: 'get_unread_count', confidence: 0.9 };
    }
    return { intent: 'read_emails', confidence: 0.7 };
  }
  
  // Intenções de agenda específicas
  if (lower.includes('agenda') || lower.includes('calendário') || lower.includes('calendar')) {
    if (lower.match(/\b(escrev|cri|cria|faz|gera|salva|anota)\b/)) {
      return { intent: 'create_agenda', confidence: 0.9 };
    }
    if (lower.match(/\b(ler|mostr|veja|ver)\b/)) {
      return { intent: 'read_agenda', confidence: 0.8 };
    }
    return { intent: 'agenda', confidence: 0.6 };
  }
  
  return null;
};

export const parseAgentCommand = (message: string): ParsedCommand | null => {
  const lower = message.toLowerCase();
  
  // Detectar intenção primeiro
  const intent = detectIntent(message);
  
  // Padrões de detecção melhorados
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
      triggers: [
        'escrever arquivo', 'criar arquivo', 'salvar arquivo', 'write file', 'create file',
        'escreva', 'escrev', 'cria', 'crie', 'faz', 'faça', 'gera', 'gerar', 'salva', 'salvar',
        'anota', 'anotar', 'criar', 'escrever'
      ],
      extractPath: (msg: string) => {
        // Múltiplos padrões para detectar caminho
        const patterns = [
          /(?:arquivo|file|documento|doc)[:\s]+([^\s"']+)/i,
          /(?:em|to|para|in|at)[:\s]+([^\s"']+)/i,
          /([A-Z]:[^\s"']+)/,
          /(\.\/[^\s"']+)/,
          /(\/[^\s"']+)/,
          /(?:chamado|called|named)[:\s]+([^\s"']+)/i,
        ];
        
        for (const pattern of patterns) {
          const match = msg.match(pattern);
          if (match) return match[1];
        }
        
        // Se mencionou "agenda", criar arquivo agenda
        if (lower.includes('agenda') || lower.includes('calendário')) {
          return 'agenda.md';
        }
        
        return null;
      },
      extractContent: (msg: string) => {
        // Múltiplos padrões para extrair conteúdo
        const patterns = [
          /com conteúdo[:\s]+"([^"]+)"/i,
          /content[:\s]+"([^"]+)"/i,
          /"([^"]+)"/,
          /com[:\s]+"([^"]+)"/i,
          /: "([^"]+)"/,
          /(?:dizendo|diz|com o texto)[:\s]+"([^"]+)"/i,
        ];
        
        for (const pattern of patterns) {
          const match = msg.match(pattern);
          if (match) return match[1];
        }
        
        // Se for sobre agenda, gerar conteúdo da agenda
        if (lower.includes('agenda') || lower.includes('calendário')) {
          return generateAgendaContent(msg);
        }
        
        return null;
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
    {
      tool: 'read_emails',
      triggers: ['ler email', 'ler emails', 'ler e-mail', 'mostrar email', 'listar email', 'emails', 'e-mails'],
      extractLimit: (msg: string) => {
        const limitMatch = msg.match(/(?:últimos|last|recentes|recent)[:\s]+(\d+)/i);
        return limitMatch ? parseInt(limitMatch[1]) : 10;
      },
    },
    {
      tool: 'search_emails',
      triggers: ['buscar email', 'procurar email', 'encontrar email', 'search email'],
      extractQuery: (msg: string) => {
        // Extrair query após "por", "de", "com", etc
        const queryMatch = msg.match(/(?:por|de|com|about|from)[:\s]+([^\s]+)/i) ||
                          msg.match(/"([^"]+)"/);
        return queryMatch ? queryMatch[1] : null;
      },
    },
    {
      tool: 'get_unread_count',
      triggers: ['emails não lidos', 'unread emails', 'novos emails', 'quantos emails'],
    },
  ];

  // Se detectou intenção de agenda, criar comando específico
  if (intent && intent.intent === 'create_agenda') {
    const agendaContent = generateAgendaContent(message);
    return {
      tool: 'write_file',
      parameters: {
        filePath: 'agenda.md',
        content: agendaContent,
      },
      requiresConfirmation: true,
      detected: true,
    };
  }
  
  // Se detectou intenção de ler agenda
  if (intent && intent.intent === 'read_agenda') {
    return {
      tool: 'read_file',
      parameters: {
        filePath: 'agenda.md',
      },
      requiresConfirmation: false,
      detected: true,
    };
  }
  
  // Se detectou intenção de ler emails
  if (intent && intent.intent === 'read_emails') {
    const limit = message.match(/(?:últimos|last|recentes|recent)[:\s]+(\d+)/i);
    return {
      tool: 'read_emails',
      parameters: {
        limit: limit ? parseInt(limit[1]) : 10,
      },
      requiresConfirmation: false,
      detected: true,
    };
  }
  
  // Se detectou intenção de buscar emails
  if (intent && intent.intent === 'search_emails') {
    const queryMatch = message.match(/(?:por|de|com|about|from)[:\s]+([^\s]+)/i) ||
                      message.match(/"([^"]+)"/);
    if (queryMatch) {
      return {
        tool: 'search_emails',
        parameters: {
          query: queryMatch[1],
          limit: 10,
        },
        requiresConfirmation: false,
        detected: true,
      };
    }
  }
  
  // Se detectou intenção de contar não lidos
  if (intent && intent.intent === 'get_unread_count') {
    return {
      tool: 'get_unread_count',
      parameters: {},
      requiresConfirmation: false,
      detected: true,
    };
  }

  for (const pattern of patterns) {
    for (const trigger of pattern.triggers) {
      if (lower.includes(trigger) || (intent && pattern.tool === intent.intent)) {
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

// Gerar conteúdo de agenda baseado na mensagem
function generateAgendaContent(message: string): string {
  const today = new Date();
  const dateStr = today.toLocaleDateString('pt-BR', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
  
  return `# Agenda - ${dateStr}

## Eventos do Dia

- [ ] 

## Tarefas

- [ ] 

## Notas

---

*Agenda criada automaticamente pelo SuperEzio*
`;
}

