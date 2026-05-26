import { createContext, useContext, useEffect, useRef, type ReactNode } from "react";
import { useQueryStream, type UseQueryStream } from "../hooks/useQueryStream";
import { save as saveSession } from "../storage/sessions";

const ActiveRunContext = createContext<UseQueryStream | null>(null);

export function ActiveRunProvider({ children }: { children: ReactNode }) {
  const run = useQueryStream();
  const persistedRef = useRef<string | null>(null);

  const { status, runId, query, startedAt, events } = run;

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

  return <ActiveRunContext.Provider value={run}>{children}</ActiveRunContext.Provider>;
}

export function useActiveRun(): UseQueryStream {
  const ctx = useContext(ActiveRunContext);
  if (!ctx) throw new Error("useActiveRun must be used within ActiveRunProvider");
  return ctx;
}
