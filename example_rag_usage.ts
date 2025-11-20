/**
 * EXEMPLO DE USO COMPLETO - RAG + Backend Python
 * 
 * Demonstra o fluxo completo:
 * 1. Adicionar informações permanentes
 * 2. Buscar contexto relevante
 * 3. Enviar para o modelo com RAG injection
 */

import { persistentRAG } from './src/services/persistentRAG.js';

console.log('\n' + '='.repeat(80));
console.log('🤖 EXEMPLO DE USO COMPLETO - RAG + Modelo');
console.log('='.repeat(80));

// Simulação de perguntas do usuário
const questions = [
  'Qual universidade o Rapha estuda?',
  'Qual o time favorito do Rapha?',
  'O que o Rapha gosta de comer?',
  'Quem é o Marco?'
];

console.log('\n📝 INFORMAÇÕES JÁ ARMAZENADAS (PERMANENTEMENTE):');
const allEntries = persistentRAG.listAll();
console.log(`Total: ${allEntries.length} entradas\n`);
allEntries.forEach((entry, idx) => {
  console.log(`${idx + 1}. ${entry.content.substring(0, 80)}...`);
  console.log(`   Tags: ${entry.tags.join(', ')}\n`);
});

console.log('='.repeat(80));
console.log('🔍 SIMULAÇÃO DE PERGUNTAS COM RAG\n');

for (const question of questions) {
  console.log('-'.repeat(80));
  console.log(`❓ PERGUNTA: ${question}\n`);
  
  // 1. Buscar contexto relevante
  const ragContext = persistentRAG.buildRagContext(question, 3);
  
  if (ragContext) {
    console.log('📋 CONTEXTO RAG ENCONTRADO:\n');
    console.log(ragContext);
    console.log();
    
    // 2. Payload que seria enviado ao backend
    const payload = {
      messages: [
        {
          role: 'user',
          content: question,
          rag_context: ragContext  // ← Contexto injetado aqui
        }
      ],
      max_tokens: 100,
      temperature: 0.3
    };
    
    console.log('📤 PAYLOAD PARA O BACKEND:');
    console.log(JSON.stringify(payload, null, 2));
    console.log();
    
    console.log('🔄 PRÓXIMO PASSO: POST http://localhost:8000/chat');
    console.log('   O backend irá injetar o RAG context no prompt do modelo');
    console.log('   O modelo responderá usando as informações do contexto');
    
  } else {
    console.log('⚠️  Nenhum contexto RAG encontrado para esta pergunta');
    console.log('   O modelo responderá sem contexto adicional');
  }
  
  console.log();
}

console.log('='.repeat(80));
console.log('✅ DEMONSTRAÇÃO COMPLETA!');
console.log();
console.log('📌 COMO USAR NA PRÁTICA:');
console.log();
console.log('1. ADICIONAR INFORMAÇÕES (uma vez):');
console.log('   persistentRAG.addMemory("Rapha estuda na UdeM", ["rapha", "educacao"])');
console.log();
console.log('2. BUSCAR CONTEXTO (a cada pergunta):');
console.log('   const context = persistentRAG.buildRagContext(userQuestion, 5)');
console.log();
console.log('3. ENVIAR AO MODELO (com RAG injection):');
console.log('   fetch("http://localhost:8000/chat", {');
console.log('     method: "POST",');
console.log('     body: JSON.stringify({');
console.log('       messages: [{ role: "user", content: question, rag_context: context }]');
console.log('     })');
console.log('   })');
console.log();
console.log('💾 PERSISTÊNCIA: Informações salvas em data/rag_memory.json');
console.log('🔄 CARREGAMENTO: Automático no startup do servidor');
console.log('='.repeat(80) + '\n');
