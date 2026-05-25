import { Wrench, Check } from "lucide-react";

interface ToolEventLineProps {
  kind: "call" | "result";
  tool: string;
  payload: unknown;
}

const MAX_LEN = 400;

function preview(payload: unknown): string {
  if (payload == null) return "";
  const text = typeof payload === "string" ? payload : JSON.stringify(payload);
  return text.length > MAX_LEN ? `${text.slice(0, MAX_LEN)}…` : text;
}

export function ToolEventLine({ kind, tool, payload }: ToolEventLineProps) {
  const isCall = kind === "call";
  const Icon = isCall ? Wrench : Check;
  const colorClass = isCall
    ? "text-amber-700 bg-amber-50 border-amber-200"
    : "text-green-700 bg-green-50 border-green-200";
  const label = isCall ? "call" : "result";
  const text = preview(payload);

  return (
    <div className={`text-xs px-2 py-1.5 rounded border ${colorClass}`}>
      <div className="flex items-center gap-2">
        <Icon className="w-3.5 h-3.5 flex-shrink-0" />
        <span className="font-mono font-medium">{tool}</span>
        <span className="ml-auto text-[10px] uppercase tracking-wide font-medium opacity-60">
          {label}
        </span>
      </div>
      {text && (
        <div className="font-mono text-gray-700 break-words mt-1 line-clamp-1 leading-snug">
          {text}
        </div>
      )}
    </div>
  );
}
