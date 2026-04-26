import { useCallback, useEffect, useRef, useState } from "react";
import { streamQuery } from "../api/stream";
import { SSE_EVENTS, type StreamEvent } from "../api/events";

export type StreamStatus = "idle" | "streaming" | "done" | "error";

interface UseQueryStream {
  events: StreamEvent[];
  status: StreamStatus;
  error: Error | null;
  submit: (query: string) => void;
  reset: () => void;
}

export function useQueryStream(): UseQueryStream {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [status, setStatus] = useState<StreamStatus>("idle");
  const [error, setError] = useState<Error | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    controllerRef.current?.abort();
    controllerRef.current = null;
    setEvents([]);
    setStatus("idle");
    setError(null);
  }, []);

  const submit = useCallback((query: string) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setEvents([]);
    setError(null);
    setStatus("streaming");

    (async () => {
      try {
        for await (const ev of streamQuery(query, controller.signal)) {
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
  }, []);

  useEffect(() => () => controllerRef.current?.abort(), []);

  return { events, status, error, submit, reset };
}
