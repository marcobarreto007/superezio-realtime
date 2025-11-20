/**
 * Componente ChatMessage Refatorado
 * Renderiza diferentes tipos de conteúdo: texto, imagem, logs de agente e ferramentas.
 */

import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { Message } from '../types/chat';
import { ExpertBadge } from './ExpertBadge';
import { Bot, User, Wrench, BrainCircuit } from 'lucide-react';

const AgentLog = ({ log }: { log: string }) => {
  return (
    <div className="text-xs text-cyan-300/70 my-1 p-2 bg-cyan-900/20 rounded-md font-mono flex items-start gap-2">
      <BrainCircuit size={14} className="flex-shrink-0 mt-0.5" />
      <span>{log}</span>
    </div>
  );
};

const ToolLog = ({ log }: { log: string }) => {
  return (
    <div className="text-xs text-amber-300/70 my-1 p-2 bg-amber-900/20 rounded-md font-mono flex items-start gap-2">
      <Wrench size={14} className="flex-shrink-0 mt-0.5" />
      <span>{log}</span>
    </div>
  );
};

const ImageAttachment = ({ src }: { src: string }) => (
    <div className="mt-2">
        <img src={src} alt="Attachment" className="rounded-lg max-w-xs max-h-64 object-cover" />
    </div>
);

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  const renderContent = (content: string) => {
    // Regex para detectar logs de CrewAI
    const agentLogRegex = /^(>\s)?(Entering new CrewAgent|Invoking|Executing|Passing|Finished|✅|DEBUG|INFO|WARNING|ERROR)/m;
    const toolLogRegex = /🔧/
    
    if (agentLogRegex.test(content) || toolLogRegex.test(content)) {
        const lines = content.split('\n');
        return (
            <div>
                {lines.map((line, index) => {
                    if (line.match(agentLogRegex)) return <AgentLog key={index} log={line} />;
                    if (line.match(toolLogRegex)) return <ToolLog key={index} log={line} />;
                    return <p key={index} className="text-sm">{line}</p>;
                })}
            </div>
        )
    }

    return (
      <ReactMarkdown
        components={{
          code(props: any) {
            const { inline, className, children } = props;
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <SyntaxHighlighter
                style={oneDark as any}
                language={match[1]}
                PreTag="div"
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            ) : (
              <code className="bg-gray-700/50 text-red-300 px-1 py-0.5 rounded text-sm font-mono">
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  return (
    <div className={`flex items-start gap-3 my-4`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'bg-blue-600' : 'bg-gray-700'}`}>
            {isUser ? <User size={18} /> : <Bot size={18} />}
        </div>
      <div className={`max-w-[85%] rounded-lg px-4 py-3 ${isUser ? 'bg-blue-600/20' : 'bg-gray-800'}`}>
        {message.image && <ImageAttachment src={message.image} />}
        {renderContent(message.content)}
        {!isUser && (message.expert || message.loraAdapter || message.mode) && (
          <ExpertBadge expert={message.expert} loraAdapter={message.loraAdapter} mode={message.mode} />
        )}
      </div>
    </div>
  );
}