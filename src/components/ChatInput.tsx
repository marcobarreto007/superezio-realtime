import { useState, useRef, useEffect } from 'react';
import { Paperclip, X } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string, image?: File) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled, placeholder = 'Manda aí...' }: ChatInputProps) {
  const [input, setInput] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  // Handle image selection
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if(fileInputRef.current) {
        fileInputRef.current.value = "";
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((input.trim() || imageFile) && !disabled) {
      onSend(input.trim(), imageFile || undefined);
      setInput('');
      clearImage();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-700 p-4">
      {/* Image Preview */}
      {imagePreview && (
        <div className="mb-2 relative w-24 h-24">
            <img src={imagePreview} alt="Preview" className="rounded-lg object-cover w-full h-full" />
            <button
                type="button"
                onClick={clearImage}
                className="absolute top-0 right-0 bg-gray-800/70 text-white rounded-full p-1 hover:bg-gray-700"
                aria-label="Remove image"
            >
                <X size={16} />
            </button>
        </div>
      )}

      <div className="flex items-end gap-2">
        <input 
            type="file" 
            ref={fileInputRef}
            onChange={handleImageChange}
            accept="image/*"
            className="hidden"
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="p-3 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
          aria-label="Attach image"
        >
          <Paperclip size={20} />
        </button>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50 max-h-32"
        />
        <button
          type="submit"
          disabled={(!input.trim() && !imageFile) || disabled}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold"
        >
          Enviar
        </button>
      </div>
      <div className="mt-2 text-xs text-gray-500">
        Enter pra enviar • Shift+Enter pra quebra de linha
      </div>
    </form>
  );
}
