/**
 * TESTE DO SISTEMA RAG PERMANENTE
 * Demonstra como armazenar informações PARA SEMPRE
 */

import { persistentRAG } from './src/services/persistentRAG.js';

console.log('\n' + '='.repeat(80));
console.log('🧪 TESTE DO SISTEMA RAG PERMANENTE');
console.log('='.repeat(80));

// 1. Adicionar informações sobre a família
console.log('\n📝 1. ADICIONANDO INFORMAÇÕES PERMANENTES...\n');

const id1 = persistentRAG.addMemory(
  'Rapha BARRETO é filho do Marco. Universitário na UdeM (Université de Montréal), curso de Ciências Políticas→Direito. Notas sempre A/A+. FÃ FANÁTICO dos Edmonton Oilers 🏒',
  ['familia', 'rapha', 'educacao'],
  { pessoa: 'Rapha', categoria: 'perfil' }
);

const id2 = persistentRAG.addMemory(
  'Marco BARRETO é o pai do Rapha. Empresário, especialista em contabilidade canadense e CRA. Mora em Montreal, Quebec. Trabalha com declarações de imposto de renda.',
  ['familia', 'marco', 'profissional'],
  { pessoa: 'Marco', categoria: 'perfil' }
);

const id3 = persistentRAG.addMemory(
  'Edmonton Oilers é o time de hockey favorito do Rapha. NHL - National Hockey League. Time do Canadá.',
  ['rapha', 'hobbies', 'esportes'],
  { pessoa: 'Rapha', categoria: 'interesses' }
);

const id4 = persistentRAG.addMemory(
  'Rapha adora sushi, especialmente salmon nigiri e spicy tuna roll. Come no Mikado e no Iroha pelo menos 2x por semana.',
  ['rapha', 'comida', 'hobbies'],
  { pessoa: 'Rapha', categoria: 'interesses' }
);

const id5 = persistentRAG.addMemory(
  'Rapha joga League of Legends nas horas vagas. Main: Top Lane (Garen, Darius). Rank: Gold II.',
  ['rapha', 'games', 'hobbies'],
  { pessoa: 'Rapha', categoria: 'interesses' }
);

console.log(`\n✅ ${5} informações armazenadas PERMANENTEMENTE!`);

// 2. Buscar informações
console.log('\n' + '='.repeat(80));
console.log('🔍 2. BUSCANDO INFORMAÇÕES...\n');

console.log('📊 Busca 1: "Quem é o Rapha?"\n');
const search1 = persistentRAG.search('Rapha universidade estudos', 5);
search1.forEach(result => {
  console.log(`   Relevância: ${(result.relevance * 100).toFixed(0)}%`);
  console.log(`   Conteúdo: ${result.content}`);
  console.log(`   Tags: ${result.tags.join(', ')}`);
  console.log();
});

console.log('📊 Busca 2: "O que o Rapha gosta de comer?"\n');
const search2 = persistentRAG.search('Rapha comida gosta comer', 5);
search2.forEach(result => {
  console.log(`   Relevância: ${(result.relevance * 100).toFixed(0)}%`);
  console.log(`   Conteúdo: ${result.content}`);
  console.log(`   Tags: ${result.tags.join(', ')}`);
  console.log();
});

console.log('📊 Busca 3: "Qual o time do Rapha?"\n');
const search3 = persistentRAG.search('Rapha time esporte hockey', 5);
search3.forEach(result => {
  console.log(`   Relevância: ${(result.relevance * 100).toFixed(0)}%`);
  console.log(`   Conteúdo: ${result.content}`);
  console.log(`   Tags: ${result.tags.join(', ')}`);
  console.log();
});

// 3. Buscar por tags
console.log('='.repeat(80));
console.log('🏷️  3. BUSCANDO POR TAGS...\n');

const byTags = persistentRAG.getByTags(['rapha', 'hobbies']);
console.log(`Encontradas ${byTags.length} entradas com tags 'rapha' OU 'hobbies':\n`);
byTags.forEach(entry => {
  console.log(`   - ${entry.content.substring(0, 80)}...`);
  console.log(`     Tags: ${entry.tags.join(', ')}\n`);
});

// 4. Criar contexto RAG formatado
console.log('='.repeat(80));
console.log('📋 4. CONTEXTO RAG FORMATADO PARA O MODELO...\n');

const context = persistentRAG.buildRagContext('Me fale sobre o Rapha', 3);
console.log(context);

// 5. Estatísticas
console.log('\n' + '='.repeat(80));
console.log('📊 5. ESTATÍSTICAS DA MEMÓRIA PERMANENTE\n');

const stats = persistentRAG.getStats();
console.log(`Total de entradas: ${stats.totalEntries}`);
console.log(`Total de tags únicas: ${stats.totalTags}`);
console.log(`Entrada mais antiga: ${new Date(stats.oldestEntry).toLocaleString()}`);
console.log(`Entrada mais recente: ${new Date(stats.newestEntry).toLocaleString()}`);

console.log('\n' + '='.repeat(80));
console.log('✅ TESTE COMPLETO!');
console.log('💾 Todas as informações estão salvas em: data/rag_memory.json');
console.log('🔄 As informações persistem entre reinicializações do servidor!');
console.log('='.repeat(80) + '\n');
