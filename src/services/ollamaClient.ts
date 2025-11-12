import { getOllamaBaseUrl, getOllamaModel } from '@/config/env';
import { Message } from '@/types';
import { ragService } from './ragService';
import { getWeather, getCryptoPrice, formatWeatherInfo, formatCryptoInfo } from './externalAPIs';
import { agentService } from './agentService';
import { searchWeb, formatSearchResults } from './webSearch';

const SYSTEM_PROMPT = `Você é SuperEzio, uma IA assistente com personalidade marcante.

PERSONALIDADE E ESTILO:
- Comunicação DIRETA, coloquial e sem floreios, em português do Brasil
- Levemente cético, pragmático e NÃO bajula o usuário
- Respostas OBJETIVAS, focadas e eficientes
- NÃO faça perguntas casuais desnecessárias (clima, como está, etc)
- NÃO seja excessivamente verboso ou empolgado
- Vai direto ao ponto - sem rodeios
- Quando não sabe algo, admite sem inventar
- Prefere soluções práticas sobre teorias

CONTEXTO DO USUÁRIO (MARCO BARRETO):
- Nome: Marco Barreto
- Localização: Montréal, Canadá (brasileiro)
- Trabalho atual: Technicien en collecte de données na CDT
- Trabalho anterior: Hayes/Instech (Vinci) - saiu em 2025-10-09
- Projetos: SuperEzio, TrafficAI, BEBE-IA, Xubudget
- Áreas: IA, trading, desenvolvimento
- Prefere: terminal, scripts, automação
- Perfil técnico - não precisa de explicações básicas

FAMÍLIA:
- Esposa: Ana Paula - personalidade forte, super organizada, "rainha da casa"
  - Trabalho: Analista júnior no ONF/NFB
- Filhos:
  - Rapha: Ciências Políticas na Université de Montréal
  - Alice: 3ª série do secundário (Sec 3)
- Cachorro: Mike - "yorke", late muito, xodó da família

AMIGOS PRÓXIMOS:
- Marcelo Alves
- Frederico Araujo

CAPACIDADES DO AGENTE (SUPER PODERES):
- Você tem acesso TOTAL aos arquivos do sistema de Marco
- Pode LER qualquer arquivo automaticamente quando mencionado
- Pode MODIFICAR arquivos (só com confirmação explícita "ok")
- Pode CRIAR arquivos e diretórios
- Pode DELETAR arquivos (com confirmação)
- Pode BUSCAR arquivos por nome/padrão
- Pode CRIAR TABELAS (HTML/CSV) a partir de dados
- Pode CRIAR AGENDAS automaticamente quando solicitado
- Pode LER EMAILS da caixa de entrada de Marco
- Pode BUSCAR emails por assunto ou remetente
- Pode CONTAR emails não lidos
- Pode BUSCAR NA INTERNET para informações atualizadas
- Pode CONSULTAR a web quando não souber algo ou precisar de dados recentes
- Pode EXPORTAR para Google Sheets (quando configurado)
- Todas as modificações requerem confirmação do usuário

ACESSO À INTERNET E BUSCA WEB:
- Você TEM ACESSO à internet e pode buscar informações em tempo real
- Quando NÃO SOUBER algo ou precisar de informações ATUALIZADAS → BUSQUE na internet automaticamente
- Quando Marco perguntar sobre eventos recentes, notícias, dados atuais → BUSQUE na web
- Quando perguntar "que dia é hoje", "data atual", "hora" → Use informações atualizadas
- Quando perguntar sobre algo que pode ter mudado → BUSQUE para ter certeza
- SEMPRE busque na internet se a informação não estiver na sua memória ou for sobre eventos recentes
- Use os resultados da busca para dar respostas precisas e atualizadas

LINGUAGEM NATURAL - ENTENDA INTENÇÕES:
- Quando Marco pedir "agenda" ou "escrever agenda" → CRIE arquivo agenda.md automaticamente
- Quando pedir "ler agenda" → LEIA agenda.md
- Quando pedir "escrever" ou "criar" algo → ENTENDA o contexto e crie o arquivo
- Quando mencionar um arquivo (ex: "package.json") → LEIA automaticamente se relevante
- Quando pedir "ler emails" ou "mostrar emails" → LEIA emails recentes automaticamente
- Quando pedir "buscar email por X" → BUSQUE emails por assunto/remetente
- Quando pedir "quantos emails não lidos" → CONTE emails não lidos
- Seja PROATIVO: se Marco pedir algo que requer arquivo ou email, execute a ação
- Use linguagem natural: "escreva agenda" = criar agenda.md, "mostra emails" = ler emails

DIRETRIZES DE RESPOSTA:
- Seja útil e direto - sem conversa fiada
- Para "oi" ou saudações simples, responda de forma breve e direta
- NÃO pergunte sobre clima, como está o dia, etc - isso é desnecessário
- Quando apropriado, sugira comandos ou scripts
- Mantenha respostas CONCISAS
- Se a pergunta for vaga, peça esclarecimento de forma direta
- Trate Marco como alguém técnico que valoriza eficiência
- Use exemplos práticos quando relevante, especialmente terminal/scripts
- Se precisar modificar arquivos, SEMPRE peça confirmação primeiro
- Quando ler arquivos, seja objetivo e direto sobre o conteúdo
- Quando NÃO SOUBER algo → BUSQUE na internet automaticamente antes de responder
- Para perguntas sobre data, hora, eventos recentes → BUSQUE informações atualizadas
- Use resultados de busca web para dar respostas precisas e atualizadas

REGRA CRÍTICA - ARQUIVOS LIDOS:
- Quando você ver [ARQUIVO LIDO - nome_arquivo] no contexto → USE O CONTEÚDO REAL DO ARQUIVO
- NÃO INVENTE conteúdo de arquivos
- NÃO ALUCINE dados que não estão no arquivo
- Se o arquivo foi lido, MOSTRE O CONTEÚDO REAL, não invente
- Se não conseguir ler o arquivo, diga honestamente "Não consegui ler o arquivo X"
- NUNCA invente conteúdo de package.json, App.tsx ou qualquer arquivo

EXEMPLOS:
❌ EVITAR: "Olá Marco! Como está o clima lá no Canadá? Vendo as previsões, parece um pouco nebuloso hoje. Você gosta de dias nublados..."
✅ CORRETO: "Oi. O que precisa?"

❌ EVITAR: "Que prazer ajudá-lo! Vou te ensinar uma forma maravilhosa..."
✅ CORRETO: "Pra isso, use \`comando\`. Se precisar de mais contexto, adiciona \`-flag\`."`;

interface OllamaMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface OllamaRequest {
  model: string;
  messages: OllamaMessage[];
  stream: boolean;
}

interface OllamaResponse {
  message: OllamaMessage;
  done: boolean;
}

export const sendMessageToOllama = async (history: Message[], modelOverride?: string): Promise<string> => {
  const baseUrl = getOllamaBaseUrl();
  const model = modelOverride || getOllamaModel();
  const url = `${baseUrl}/api/chat`;

  // Última mensagem do usuário
  const lastUserMessage = history[history.length - 1];
  
  // Verificar se precisa de APIs externas
  let enhancedMessage = lastUserMessage.content;
  const lowerContent = lastUserMessage.content.toLowerCase();
  
  if (lowerContent.includes('clima') || lowerContent.includes('temperatura') || lowerContent.includes('weather') || 
      lowerContent.includes('temperatura em') || lowerContent.includes('temperatura de')) {
    // Extrair cidade se mencionada
    const cityMatch = lowerContent.match(/(?:em|de|em|na|no)\s+([a-záàâãéêíóôõúç]+)/i);
    const city = cityMatch ? cityMatch[1] : 'Montreal';
    
    const weather = await getWeather(city);
    if (weather) {
      enhancedMessage += `\n\n[Info Clima REAL - ${weather.city}]: ${formatWeatherInfo(weather)}`;
    } else {
      // Se falhar, ser honesto
      enhancedMessage += `\n\n[AVISO]: Não consegui buscar dados de clima para ${city}. A API pode estar temporariamente indisponível.`;
    }
  }
  
  if (lowerContent.includes('bitcoin') || lowerContent.includes('btc') || lowerContent.includes('cripto') || lowerContent.includes('crypto')) {
    const crypto = await getCryptoPrice('BTC');
    if (crypto) {
      enhancedMessage += `\n\n[Info Cripto]: ${formatCryptoInfo(crypto)}`;
    }
  }

  // Verificar se precisa usar tools do agente - LINGUAGEM NATURAL MELHORADA
  const lowerMessage = enhancedMessage.toLowerCase();
  let agentContext = '';
  
  // Detectar intenção de listar diretório
  if (lowerMessage.match(/\b(listar|lista|mostrar|mostra|arquivos|files|pasta|diretorio|directory|folder)\b/)) {
    const dirMatch = lowerMessage.match(/(?:pasta|diretorio|directory|folder|em|in)[:\s]+([^\s"']+)/i) ||
                    lowerMessage.match(/(\.\/[^\s"']+)/) ||
                    lowerMessage.match(/([A-Z]:[^\s"']+)/);
    if (dirMatch) {
      const dirPath = dirMatch[1];
      const dirContent = await agentService.listDirectory(dirPath);
      if (dirContent && dirContent.length > 0) {
        agentContext += `\n\n[Conteúdo do diretório ${dirPath}]:\n${dirContent.map((item: any) => 
          `${item.type === 'directory' ? '📁' : '📄'} ${item.name} ${item.type === 'file' ? `(${item.size} bytes)` : ''}`
        ).join('\n')}`;
      } else if (dirContent && dirContent.formatted) {
        agentContext += `\n\n[Conteúdo do diretório ${dirPath}]:\n${dirContent.formatted}`;
      }
    }
  }

  // Detectar menções de arquivos (linguagem natural) - MELHORADO
  const fileMentions = [
    // Padrões específicos primeiro
    /(?:ler|leia|mostr|mostra|abre|abrir|veja|ver|exibe|exibir|conteúdo|conteudo)[:\s]+(?:do|de|o|a)[:\s]+([^\s"']+\.(txt|json|csv|js|ts|py|md|jsx|tsx|html|css))/i,
    /(?:arquivo|file)[:\s]+([^\s"']+\.(txt|json|csv|js|ts|py|md|jsx|tsx|html|css))/i,
    // Arquivos mencionados diretamente (package.json, App.tsx, etc)
    /\b(package\.json|package-lock\.json|tsconfig\.json|vite\.config\.ts|App\.tsx|index\.tsx|README\.md|\.env\.local)\b/i,
    // Caminhos absolutos
    /([A-Z]:[^\s"']+\.(txt|json|csv|js|ts|py|md|jsx|tsx|html|css))/i,
    // Caminhos relativos
    /(\.\/[^\s"']+\.(txt|json|csv|js|ts|py|md|jsx|tsx|html|css))/i,
    /(\/[^\s"']+\.(txt|json|csv|js|ts|py|md|jsx|tsx|html|css))/i,
  ];
  
  for (const pattern of fileMentions) {
    const match = enhancedMessage.match(pattern);
    if (match) {
      const filePath = match[1] || match[0]; // Pegar o arquivo mencionado
      if (filePath) {
        const fileContent = await agentService.readFile(filePath);
        if (fileContent) {
          agentContext += `\n\n[ARQUIVO LIDO - ${filePath}]:\n${fileContent.substring(0, 3000)}\n\n[FIM DO ARQUIVO ${filePath}]`;
          break; // Só ler um arquivo por vez
        } else {
          // Se falhou, avisar
          agentContext += `\n\n[AVISO]: Não consegui ler o arquivo ${filePath}. Verifique se o caminho está correto.`;
        }
      }
    }
  }
  
  // Detectar intenção de agenda
  if (lowerMessage.includes('agenda') || lowerMessage.includes('calendário')) {
    if (lowerMessage.match(/\b(escrev|escreva|cri|cria|crie|faz|faça|gera|gerar|salva|salvar|anota|anotar)\b/)) {
      // Vai criar agenda - o parser vai detectar
      agentContext += '\n\n[Intenção detectada: Criar agenda. O sistema vai criar agenda.md automaticamente.]';
    } else if (lowerMessage.match(/\b(ler|leia|mostr|mostra|veja|ver)\b/)) {
      // Tentar ler agenda
      const agendaContent = await agentService.readFile('agenda.md');
      if (agendaContent) {
        agentContext += `\n\n[Agenda atual]:\n${agendaContent.substring(0, 2000)}`;
      }
    }
  }
  
  // Detectar intenção de email
  if (lowerMessage.includes('email') || lowerMessage.includes('e-mail') || lowerMessage.includes('correio')) {
    if (lowerMessage.match(/\b(ler|leia|mostr|mostra|veja|ver|listar|lista)\b/)) {
      const limit = lowerMessage.match(/(?:últimos|last|recentes|recent)[:\s]+(\d+)/i);
      const emails = await agentService.readEmails(limit ? parseInt(limit[1]) : 10);
      if (emails && emails.length > 0) {
        agentContext += `\n\n[Emails recentes (${emails.length}):\n${emails.map((e, i) => 
          `${i + 1}. De: ${e.from}\n   Assunto: ${e.subject}\n   Data: ${e.date}\n   ${e.text?.substring(0, 200) || ''}`
        ).join('\n\n')}]`;
      }
    } else if (lowerMessage.match(/\b(não lido|unread|novo|novos|quantos)\b/)) {
      const count = await agentService.getUnreadCount();
      agentContext += `\n\n[Emails não lidos: ${count}]`;
    }
  }

  // Detectar necessidade de busca web (mais seletivo)
  let webSearchResults: string | undefined;
  const needsWebSearch = 
    lowerMessage.includes('que dia é') || 
    lowerMessage.includes('data atual') || 
    lowerMessage.includes('hoje é') ||
    lowerMessage.includes('que dia') ||
    lowerMessage.includes('que hora') ||
    lowerMessage.includes('que data') ||
    lowerMessage.match(/\b(quando foi|quando aconteceu|recente|atual|hoje|agora|notícia|noticia|news|evento|acontecimento)\b/);
  
  if (needsWebSearch) {
    // Buscar na web para informações atualizadas
    try {
      const searchResponse = await searchWeb(enhancedMessage, 3);
      if (searchResponse.results.length > 0) {
        webSearchResults = formatSearchResults(searchResponse);
        // Salvar busca na memória RAG
        await ragService.addWebSearchToMemory(enhancedMessage, webSearchResults);
      }
    } catch (error) {
      console.error('Web search error:', error);
    }
  }

  // RAG: buscar contexto relevante (agora com busca web)
  const enhancedPrompt = await ragService.enhancePrompt(enhancedMessage + agentContext, history, webSearchResults);

  const userMessages = history.slice(0, -1).map((msg): OllamaMessage => ({
    role: msg.role === 'user' ? 'user' : 'assistant',
    content: msg.content,
  }));

  // Adicionar mensagem do usuário com contexto RAG
  userMessages.push({
    role: 'user',
    content: enhancedPrompt,
  });

  const payload: OllamaRequest = {
    model: model,
    messages: [
      { role: 'system', content: SYSTEM_PROMPT },
      ...userMessages
    ],
    stream: false,
  };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`Ollama API request failed with status ${response.status}: ${errorBody}`);
    }

    const data: OllamaResponse = await response.json();
    const responseContent = data.message.content;
    
    // Salvar na memória RAG
    if (lastUserMessage) {
      await ragService.addToMemory(lastUserMessage);
    }
    if (data.message.content) {
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        author: 'SuperEzio',
        content: responseContent,
        timestamp: new Date().toISOString(),
      };
      await ragService.addToMemory(assistantMessage);
    }
    
    return responseContent;
  } catch (error) {
    console.error('Error communicating with Ollama:', error);
    if (error instanceof Error) {
        return `Erro ao conectar com o Ollama: ${error.message}. Verifique se o serviço está rodando e acessível na URL configurada.`;
    }
    return 'Ocorreu um erro desconhecido ao tentar se comunicar com o Ollama.';
  }
};
