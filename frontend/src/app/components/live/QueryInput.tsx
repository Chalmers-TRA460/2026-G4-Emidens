import { useRef, useState, type FormEvent } from "react";
import { Send } from "lucide-react";

const MAX_HEIGHT_PX = 160;

interface QueryInputProps {
  onSubmit: (query: string) => void;
  disabled: boolean;
  placeholder?: string;
}

export function QueryInput({ onSubmit, disabled, placeholder = "Ask a clinical question…" }: QueryInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const resize = () => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, MAX_HEIGHT_PX)}px`;
  };

  const reset = () => {
    setValue("");
    const ta = textareaRef.current;
    if (ta) ta.style.height = "auto";
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    reset();
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white rounded-lg border border-gray-200 px-3 py-2 flex gap-2 items-end focus-within:border-blue-300 transition-colors"
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
          resize();
        }}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none bg-transparent text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none disabled:text-gray-400 leading-6"
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
      />
      <button
        type="submit"
        aria-label="Send"
        disabled={disabled || !value.trim()}
        className="flex items-center justify-center w-8 h-8 rounded-md bg-blue-500 text-white hover:bg-blue-600 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors shrink-0"
      >
        <Send className="w-3.5 h-3.5" />
      </button>
    </form>
  );
}
