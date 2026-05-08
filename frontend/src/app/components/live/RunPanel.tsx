import { useEffect, useRef } from "react";
import { useQueryStream } from "../../../hooks/useQueryStream";
import { QueryInput } from "./QueryInput";
import { EventView } from "./EventView";

const STATUS_LABEL: Record<string, string> = {
  idle:      "Ready",
  streaming: "Streaming…",
  done:      "Done",
  error:     "Error",
};

const STATUS_COLOR: Record<string, string> = {
  idle:      "bg-gray-100 text-gray-600",
  streaming: "bg-blue-100 text-blue-700",
  done:      "bg-green-100 text-green-700",
  error:     "bg-red-100 text-red-700",
};

interface RunPanelProps {
  title: string;
  path?: string;
  badge?: string;
  placeholder?: string;
}

export function RunPanel({ title, path, badge, placeholder }: RunPanelProps) {
  const { events, status, error, submit, reset } = useQueryStream(path);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [events.length]);

  return (
    <div className="flex flex-col bg-white rounded-lg border border-gray-200 overflow-hidden min-w-0 min-h-0">
      <div className="border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-gray-900">{title}</h2>
          {badge && (
            <span className="text-[10px] font-medium uppercase tracking-wide px-1.5 py-0.5 rounded bg-amber-100 text-amber-800">
              {badge}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className={`inline-flex px-2 py-0.5 rounded-full text-xs ${STATUS_COLOR[status]}`}>
            {STATUS_LABEL[status]}
          </span>
          {events.length > 0 && (
            <button onClick={reset} className="text-xs text-gray-500 hover:text-gray-900">
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
        <QueryInput onSubmit={submit} disabled={status === "streaming"} placeholder={placeholder} />
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg p-3">
            {error.message}
          </div>
        )}
        {events.map((ev, i) => (
          <div key={i} className="animate-fade-up">
            <EventView event={ev} />
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
