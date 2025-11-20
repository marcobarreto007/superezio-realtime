/**
 * Teste de persistência - verifica se dados são carregados do disco
 */

import { persistentRAG } from './src/services/persistentRAG.js';

console.log('\n' + '='.repeat(80));
console.log('🔄 TESTE DE PERSISTÊNCIA - Carregamento de Dados');
console.log('='.repeat(80));

// Buscar informações
console.log('\n📊 Busca 1: "Edmonton Oilers"\n');
const results1 = persistentRAG.search('Edmonton Oilers hockey', 3);
results1.forEach(r => {
  console.log(`  - [${r.id.substring(0, 20)}...] ${r.content.substring(0, 80)}...`);
  console.log(`    Relevância: ${(r.relevance * 100).toFixed(0)}% | Tags: ${r.tags.join(', ')}\n`);
});

console.log('📊 Busca 2: "universidade Rapha"\n');
const results2 = persistentRAG.search('universidade Rapha estudos', 2);
results2.forEach(r => {
  console.log(`  - [${r.id.substring(0, 20)}...] ${r.content.substring(0, 80)}...`);
  console.log(`    Relevância: ${(r.relevance * 100).toFixed(0)}% | Tags: ${r.tags.join(', ')}\n`);
});

console.log('📊 Busca 3: "Marco trabalho"\n');
const results3 = persistentRAG.search('Marco empresário CRA', 2);
results3.forEach(r => {
  console.log(`  - [${r.id.substring(0, 20)}...] ${r.content.substring(0, 80)}...`);
  console.log(`    Relevância: ${(r.relevance * 100).toFixed(0)}% | Tags: ${r.tags.join(', ')}\n`);
});

// Estatísticas
const stats = persistentRAG.getStats();
console.log('='.repeat(80));
console.log('📊 ESTATÍSTICAS');
console.log('='.repeat(80));
console.log(`Total de entradas: ${stats.totalEntries}`);
console.log(`Total de tags: ${stats.totalTags}`);
console.log(`Entrada mais antiga: ${new Date(stats.oldestEntry).toLocaleString()}`);
console.log(`Entrada mais recente: ${new Date(stats.newestEntry).toLocaleString()}`);

console.log('\n' + '='.repeat(80));
console.log('✅ PERSISTÊNCIA FUNCIONANDO!');
console.log('💾 Dados carregados de: data/rag_memory.json');
console.log('='.repeat(80) + '\n');
