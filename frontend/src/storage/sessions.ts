import type { StreamEvent } from "../api/events";

const STORAGE_KEY = "emidens.sessions.v1";
const MAX_SESSIONS = 50;

export type StoredSessionStatus = "completed" | "failed";

export interface StoredSession {
  id: string;
  query: string;
  startedAt: number;
  finishedAt: number;
  status: StoredSessionStatus;
  events: StreamEvent[];
}

function readRaw(): StoredSession[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as StoredSession[]) : [];
  } catch {
    return [];
  }
}

function writeRaw(sessions: StoredSession[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
  } catch {
    // Quota exceeded or storage disabled — silently drop. The user has live
    // data on screen; persistence is best-effort.
  }
}

export function loadAll(): StoredSession[] {
  return readRaw().sort((a, b) => b.startedAt - a.startedAt);
}

export function get(id: string): StoredSession | undefined {
  return readRaw().find((s) => s.id === id);
}

export function save(session: StoredSession): void {
  const others = readRaw().filter((s) => s.id !== session.id);
  const next = [session, ...others]
    .sort((a, b) => b.startedAt - a.startedAt)
    .slice(0, MAX_SESSIONS);
  writeRaw(next);
}

export function remove(id: string): void {
  writeRaw(readRaw().filter((s) => s.id !== id));
}

export function clear(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
