import { useEffect, useRef } from "react";
import { useQueryStream } from "../../hooks/useQueryStream";
import { SSE_EVENTS, type StreamEvent } from "../../api/events";
import { QueryInput } from "../components/live/QueryInput";
import { RoutingPanel } from "../components/live/RoutingPanel";
import { ToolEventLine } from "../components/live/ToolEventLine";
import { ExpertResponseCard } from "../components/live/ExpertResponseCard";

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

export function NewRunPage() {
  const { events, status, error, submit, reset } = useQueryStream();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [events.length]);

  return (
    <div className="flex-1 flex flex-col min-w-0">
      <div className="border-b border-gray-200 bg-white px-6 py-3.5 flex items-center justify-between">
        <h1 className="text-base font-semibold text-gray-900">New Query</h1>
        <div className="flex items-center gap-3">
          <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs ${STATUS_COLOR[status]}`}>
            {STATUS_LABEL[status]}
          </span>
          {events.length > 0 && (
            <button
              onClick={reset}
              className="text-xs text-gray-500 hover:text-gray-900"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 p-5 overflow-y-auto">
        <div className="max-w-3xl mx-auto space-y-4">
          <QueryInput onSubmit={submit} disabled={status === "streaming"} />

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
    </div>
  );
}

function EventView({ event }: { event: StreamEvent }) {
  switch (event.type) {
    case SSE_EVENTS.ROUTING:
      return <RoutingPanel payload={event.data} />;
    case SSE_EVENTS.EXPERT_RESPONSE:
      return <ExpertResponseCard payload={event.data} />;
    case SSE_EVENTS.FINAL:
      return <ExpertResponseCard payload={event.data} isFinal />;
    case SSE_EVENTS.TOOL_CALL:
      return <ToolEventLine kind="call" tool={event.data.tool} payload={event.data.input} />;
    case SSE_EVENTS.TOOL_RESULT:
      return <ToolEventLine kind="result" tool={event.data.tool} payload={event.data.output} />;
    case SSE_EVENTS.DONE:
      return null;
  }
}
