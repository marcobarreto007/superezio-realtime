export type Message = {
  id: string;
  role: 'user' | 'assistant';
  author: 'Marco' | 'SuperEzio';
  content: string;
  timestamp: string;
};