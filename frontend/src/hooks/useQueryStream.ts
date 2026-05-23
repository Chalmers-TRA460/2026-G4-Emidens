import { useCallback, useEffect, useRef, useState } from "react";
import { streamQuery, type ClinicalContext } from "../api/stream";
import { SSE_EVENTS, type StreamEvent } from "../api/events";

export type StreamStatus = "idle" | "streaming" | "done" | "error";

interface UseQueryStream {
  events: StreamEvent[];
  status: StreamStatus;
  error: Error | null;
  runId: string | null;
  query: string | null;
  startedAt: number | null;
  submit: (query: string, clinicalContext?: ClinicalContext, skippedFields?: string[]) => void;
  reset: () => void;
}

function newRunId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `run_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
}

export function useQueryStream(path: string = "/query/stream"): UseQueryStream {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [status, setStatus] = useState<StreamStatus>("idle");
  const [error, setError] = useState<Error | null>(null);
  const [runId, setRunId] = useState<string | null>(null);
  const [query, setQuery] = useState<string | null>(null);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setEvents([]);
    setStatus("idle");
    setError(null);
    setRunId(null);
    setQuery(null);
    setStartedAt(null);
  }, []);

  const submit = useCallback((nextQuery: string, clinicalContext?: ClinicalContext, skippedFields?: string[]) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setEvents([]);
    setError(null);
    setStatus("streaming");
    setRunId(newRunId());
    setQuery(nextQuery);
    setStartedAt(Date.now());

    (async () => {
      try {
        for await (const ev of streamQuery(nextQuery, controller.signal, path, clinicalContext, skippedFields)) {
          if (controller.signal.aborted) return;
          setEvents((prev) => [...prev, ev]);
          if (ev.type === SSE_EVENTS.DONE) break;
        }
        if (!controller.signal.aborted) setStatus("done");
      } catch (err) {
        if (controller.signal.aborted) return;
        setError(err instanceof Error ? err : new Error(String(err)));
        setStatus("error");
      }
    })();
  }, [path]);

  useEffect(() => () => controllerRef.current?.abort(), []);

  return { events, status, error, runId, query, startedAt, submit, reset };
}
