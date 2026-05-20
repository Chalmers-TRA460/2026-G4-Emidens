import { useEffect, useMemo, useRef } from "react";
import { useQueryStream } from "../../hooks/useQueryStream";
import type { ClinicalContext } from "../../api/stream";
import { SSE_EVENTS } from "../../api/events";
import { QueryInput } from "../components/live/QueryInput";
import { RichRunView } from "../components/RichRunView";
import { ClinicalInputForm } from "../components/live/ClinicalInputForm";
import { save as saveSession } from "../../storage/sessions";
import { deriveSessionView, type DeriveStatus } from "../../storage/derive";

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

function deriveStatusOf(s: "idle" | "streaming" | "done" | "error"): DeriveStatus {
  if (s === "done") return "completed";
  if (s === "error") return "failed";
  return "running";
}

export function NewRunPage() {
  const { events, status, error, runId, query, startedAt, submit, reset } = useQueryStream();
  const persistedRef = useRef<string | null>(null);

  const hasStarted = events.length > 0 || status === "streaming";

  useEffect(() => {
    if (status !== "done" && status !== "error") return;
    if (!runId || !query || !startedAt) return;
    if (persistedRef.current === runId) return;
    persistedRef.current = runId;
    saveSession({
      id: runId,
      query,
      startedAt,
      finishedAt: Date.now(),
      status: status === "done" ? "completed" : "failed",
      events,
    });
  }, [status, runId, query, startedAt, events]);

  const derived = useMemo(() => {
    if (!runId || !startedAt) return null;
    return deriveSessionView({
      id: runId,
      startedAt,
      finishedAt: status === "done" || status === "error" ? Date.now() : null,
      status: deriveStatusOf(status),
      events,
    });
  }, [runId, startedAt, status, events]);

  const requestedInputs = useMemo(() => {
    const seen = new Set<string>();
    const ordered: string[] = [];
    for (const ev of events) {
      if (ev.type !== SSE_EVENTS.FINAL && ev.type !== SSE_EVENTS.EXPERT_RESPONSE) continue;
      for (const f of ev.data.requested_inputs ?? []) {
        if (!seen.has(f)) {
          seen.add(f);
          ordered.push(f);
        }
      }
    }
    return ordered;
  }, [events]);

  const showInputForm =
    requestedInputs.length > 0 && status !== "streaming" && query !== null;

  const handleAnswerInputs = (ctx: ClinicalContext) => {
    if (!query) return;
    submit(query, ctx);
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 min-h-0">
      <div className="border-b border-gray-200 bg-white px-6 py-3.5 flex items-center justify-between">
        <h1 className="text-base font-semibold text-gray-900">New Query</h1>
        <div className="flex items-center gap-3">
          <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs ${STATUS_COLOR[status]}`}>
            {STATUS_LABEL[status]}
          </span>
          {hasStarted && (
            <button
              onClick={reset}
              className="text-xs text-gray-500 hover:text-gray-900"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {hasStarted && query && (
        <div className="border-b border-gray-200 bg-white px-6 py-3">
          <div className="text-xs text-gray-500 mb-1">Query</div>
          <div className="text-sm text-gray-900">{query}</div>
        </div>
      )}

      {showInputForm && (
        <div className="px-6 pt-4">
          <ClinicalInputForm
            fields={requestedInputs}
            onSubmit={handleAnswerInputs}
          />
        </div>
      )}

      {error && (
        <div className="mx-6 mt-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg p-3">
          {error.message}
        </div>
      )}

      {!hasStarted ? (
        <div className="flex-1 p-5 overflow-y-auto">
          <div className="max-w-3xl mx-auto">
            <QueryInput onSubmit={submit} disabled={false} />
          </div>
        </div>
      ) : derived ? (
        <RichRunView
          runOverview={derived.runOverview}
          agentCards={derived.agentCards}
          events={events}
          toolResults={derived.toolResults}
        />
      ) : null}

      {hasStarted && status !== "streaming" && !showInputForm && (
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="max-w-3xl mx-auto">
            <QueryInput onSubmit={submit} disabled={false} />
          </div>
        </div>
      )}
    </div>
  );
}
