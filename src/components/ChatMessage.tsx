/**
 * Componente ChatMessage
 * Exibe mensagem com markdown + code highlighting
 */

import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import type { Message } from '../types/chat'

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-800 text-gray-100'
        }`}
      >
        <ReactMarkdown
          components={{
            code(props: any) {
              const { inline, className, children } = props
              const match = /language-(\w+)/.exec(className || '')
              return !inline && match ? (
                <SyntaxHighlighter
                  style={oneDark as any}
                  language={match[1]}
                  PreTag="div"
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className="bg-gray-700 px-1 py-0.5 rounded">
                  {children}
                </code>
              )
            },
          }}
        >
          {message.content}
        </ReactMarkdown>

        {message.ragContext && message.ragContext.length > 0 && (
          <div className="mt-2 text-xs opacity-60">
            📚 RAG: {message.ragContext.length} documentos
          </div>
        )}
      </div>
    </div>
  )
}
