import { Brain } from "lucide-react";

interface ReasoningLineProps {
  text: string;
}

export function ReasoningLine({ text }: ReasoningLineProps) {
  return (
    <div className="flex items-start gap-2 text-xs px-2 py-1.5 rounded border text-indigo-700 bg-indigo-50 border-indigo-200">
      <Brain className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
      <div className="min-w-0 flex-1">
        <span className="font-medium">reasoning</span>
        <div className="text-gray-700 whitespace-pre-wrap break-words mt-0.5">{text}</div>
      </div>
    </div>
  );
}
