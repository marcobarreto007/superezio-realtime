// Test RAG query directly
import { persistentRAG } from './src/services/persistentRAG';

console.log('🔍 TESTANDO RAG QUERY\n');

// Test 1: Search HF models
console.log('Test 1: Buscar modelos Python do HF');
const models = persistentRAG.search('python code models', 5, undefined, ['hf_models_code']);
console.log(`Encontrados: ${models.length} modelos`);
models.forEach((m, i) => {
  console.log(`\n${i + 1}. ${m.id}`);
  console.log(`   Tags: ${m.tags.join(', ')}`);
  console.log(`   Content: ${m.content.substring(0, 150)}...`);
});

// Test 2: Search HF datasets
console.log('\n\nTest 2: Buscar datasets TypeScript do HF');
const datasets = persistentRAG.search('typescript dataset', 3, undefined, ['hf_datasets_code']);
console.log(`Encontrados: ${datasets.length} datasets`);
datasets.forEach((d, i) => {
  console.log(`\n${i + 1}. ${d.id}`);
  console.log(`   Tags: ${d.tags.join(', ')}`);
});

console.log('\n\nTest 3: RAG context para code_hf_curator');
const context = persistentRAG.buildRagContext(
  ['hf_models_code', 'hf_datasets_code'],
  'quais modelos de codigo python existem?',
  10
);
console.log(`Context length: ${context.length} caracteres`);
console.log(`\n${context.substring(0, 500)}...`);

console.log('\n\n✅ TODOS OS TESTES CONCLUÍDOS');
