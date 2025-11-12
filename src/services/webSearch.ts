// Serviço de busca web para SuperEzio
// Usa DuckDuckGo Instant Answer API (gratuita, sem key)

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  source?: string;
}

export interface WebSearchResponse {
  query: string;
  results: SearchResult[];
  answer?: string; // Resposta direta se disponível
}

// Buscar na web usando DuckDuckGo (gratuito, sem API key)
export async function searchWeb(query: string, limit: number = 5): Promise<WebSearchResponse> {
  try {
    // DuckDuckGo Instant Answer API
    const ddgUrl = `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json&no_html=1&skip_disambig=1`;
    
    const response = await fetch(ddgUrl);
    
    if (!response.ok) {
      throw new Error(`DuckDuckGo API error: ${response.status}`);
    }

    const data = await response.json();
    
    const results: SearchResult[] = [];
    
    // Se tiver resposta direta (Abstract)
    if (data.AbstractText) {
      results.push({
        title: data.Heading || query,
        url: data.AbstractURL || '',
        snippet: data.AbstractText,
        source: 'DuckDuckGo Instant Answer',
      });
    }
    
    // Adicionar RelatedTopics
    if (data.RelatedTopics && Array.isArray(data.RelatedTopics)) {
      for (const topic of data.RelatedTopics.slice(0, limit - results.length)) {
        if (topic.Text && topic.FirstURL) {
          results.push({
            title: topic.Text.split(' - ')[0] || topic.Text.substring(0, 50),
            url: topic.FirstURL,
            snippet: topic.Text,
            source: 'DuckDuckGo',
          });
        }
      }
    }
    
    // Se não tiver resultados suficientes, usar busca alternativa
    if (results.length < 2) {
      // Fallback: usar busca genérica (pode ser expandido)
      const fallbackResults = await searchWebFallback(query, limit);
      results.push(...fallbackResults);
    }

    return {
      query,
      results: results.slice(0, limit),
      answer: data.AbstractText || undefined,
    };
  } catch (error) {
    console.error('Error searching web:', error);
    // Fallback para busca alternativa
    return {
      query,
      results: await searchWebFallback(query, limit),
    };
  }
}

// Fallback: busca usando Wikipedia ou outras fontes
async function searchWebFallback(query: string, limit: number): Promise<SearchResult[]> {
  try {
    // Tentar Wikipedia
    const wikiUrl = `https://pt.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(query)}`;
    const wikiResponse = await fetch(wikiUrl).catch(() => null);
    
    if (wikiResponse?.ok) {
      const wikiData = await wikiResponse.json();
      if (wikiData.extract) {
        return [{
          title: wikiData.title || query,
          url: wikiData.content_urls?.desktop?.page || '',
          snippet: wikiData.extract.substring(0, 500),
          source: 'Wikipedia',
        }];
      }
    }
  } catch (error) {
    console.error('Fallback search error:', error);
  }
  
  return [];
}

// Formatar resultados para exibição
export function formatSearchResults(response: WebSearchResponse): string {
  if (response.answer) {
    return `[Resposta direta]: ${response.answer}\n\n[Fontes]:\n${response.results.map((r, i) => 
      `${i + 1}. ${r.title}\n   ${r.snippet.substring(0, 200)}...\n   ${r.url}`
    ).join('\n\n')}`;
  }
  
  if (response.results.length === 0) {
    return 'Nenhum resultado encontrado na busca.';
  }
  
  return `[Resultados da busca por "${response.query}"]:\n\n${response.results.map((r, i) => 
    `${i + 1}. ${r.title}\n   ${r.snippet.substring(0, 200)}...\n   ${r.url}`
  ).join('\n\n')}`;
}

