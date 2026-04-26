import { useState, type FormEvent } from "react";
import { Send } from "lucide-react";

interface QueryInputProps {
  onSubmit: (query: string) => void;
  disabled: boolean;
}

export function QueryInput({ onSubmit, disabled }: QueryInputProps) {
  const [value, setValue] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-3 flex gap-2 items-end">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Ask a clinical question…"
        disabled={disabled}
        rows={3}
        className="flex-1 resize-none bg-transparent text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none disabled:text-gray-400"
        onKeyDown={(e) => {
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit(e);
        }}
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-blue-500 text-white text-sm hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        <Send className="w-3.5 h-3.5" />
        Send
      </button>
    </form>
  );
}
