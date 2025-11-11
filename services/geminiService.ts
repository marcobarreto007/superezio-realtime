import { GoogleGenAI, Chat } from '@google/genai';

if (!process.env.API_KEY) {
  throw new Error("API_KEY environment variable not set");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const systemInstruction = `
You are Superezio, an advanced real-time financial assistant.
Your expertise lies in personal finance, investment strategies, and expense management.
Your tone is professional, insightful, and data-driven. You provide clear, actionable advice to help the user achieve their financial goals.
Start the conversation by introducing yourself as Superezio and asking what financial topic the user wishes to discuss.
When asked to generate a report (e.g., 'gere um relatorio'), format the data as CSV, clearly indicating the start and end of the CSV block with \`\`\`csv and \`\`\`.
Do not add any text before or after the CSV block in your response if a report is requested.
Communicate in the user's language, which appears to be Brazilian Portuguese.
`;

export const startChat = (): Chat => {
  return ai.chats.create({
    model: 'gemini-2.5-flash',
    config: {
      systemInstruction: systemInstruction,
    },
  });
};