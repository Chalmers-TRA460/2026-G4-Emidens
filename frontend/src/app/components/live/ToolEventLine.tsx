import { Wrench, Check } from "lucide-react";

interface ToolEventLineProps {
  kind: "call" | "result";
  tool: string;
  payload: unknown;
}

const MAX_LEN = 120;

function preview(payload: unknown): string {
  if (payload == null) return "";
  const text = typeof payload === "string" ? payload : JSON.stringify(payload);
  return text.length > MAX_LEN ? `${text.slice(0, MAX_LEN)}…` : text;
}

export function ToolEventLine({ kind, tool, payload }: ToolEventLineProps) {
  const isCall = kind === "call";
  const Icon = isCall ? Wrench : Check;
  const colorClass = isCall ? "text-amber-700 bg-amber-50 border-amber-200" : "text-green-700 bg-green-50 border-green-200";
  const label = isCall ? "tool call" : "result";

  return (
    <div className={`flex items-start gap-2 text-xs px-2 py-1.5 rounded border ${colorClass}`}>
      <Icon className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
      <div className="min-w-0 flex-1">
        <span className="font-medium">{tool}</span>
        <span className="text-gray-500 ml-1.5">{label}</span>
        <div className="font-mono text-gray-600 break-words mt-0.5">{preview(payload)}</div>
      </div>
    </div>
  );
}
