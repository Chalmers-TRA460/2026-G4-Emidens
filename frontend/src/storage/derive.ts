import { SSE_EVENTS, type StreamEvent, type ResponsePayload } from "../api/events";
import type { AgentCardData, AgentColor, RunOverviewData, TimelineStep } from "../types";
import { formatDuration, formatStarted } from "./format";

const AGENT_COLORS: AgentColor[] = ["blue", "green", "yellow", "purple"];

export type DeriveStatus = "completed" | "failed" | "running";

export interface DeriveInput {
  id: string;
  startedAt: number;
  finishedAt: number | null;
  status: DeriveStatus;
  events: StreamEvent[];
}

export interface DerivedSessionView {
  runOverview: RunOverviewData;
  agentCards: AgentCardData[];
}

function capitalize(s: string): string {
  return s.length === 0 ? s : s[0].toUpperCase() + s.slice(1);
}

function timeFromTrace(payload: ResponsePayload, fallback: number): string {
  const last = payload.trace[payload.trace.length - 1];
  if (last?.time) {
    try {
      return new Date(last.time).toLocaleTimeString();
    } catch {
      // ignore
    }
  }
  return new Date(fallback).toLocaleTimeString();
}

function agentLabel(capability: string): string {
  return `${capitalize(capability)} Expert`;
}

function formatResponseContent(payload: ResponsePayload): string {
  const lines = [payload.answer.trim()];
  if (payload.citations.length > 0) {
    lines.push("");
    lines.push("**Citations:**");
    for (const c of payload.citations) {
      lines.push(`- ${c.source} — ${c.section}`);
    }
  }
  return lines.join("\n");
}

export function deriveSessionView(input: DeriveInput): DerivedSessionView {
  const expertEvents: { capability: string; payload: ResponsePayload }[] = [];
  let finalEvent: ResponsePayload | undefined;
  let routingPresent = false;

  for (const ev of input.events) {
    if (ev.type === SSE_EVENTS.ROUTING) {
      routingPresent = true;
    } else if (ev.type === SSE_EVENTS.EXPERT_RESPONSE) {
      expertEvents.push({ capability: ev.data.capability, payload: ev.data });
    } else if (ev.type === SSE_EVENTS.FINAL) {
      finalEvent = ev.data;
    }
  }

  const agentCards: AgentCardData[] = expertEvents.map((e, i) => ({
    agentName: agentLabel(e.capability),
    timestamp: timeFromTrace(e.payload, input.startedAt),
    color: AGENT_COLORS[i % AGENT_COLORS.length],
    content: formatResponseContent(e.payload),
  }));

  if (finalEvent) {
    agentCards.push({
      agentName: "Synthesis",
      timestamp: timeFromTrace(finalEvent, input.finishedAt ?? Date.now()),
      color: AGENT_COLORS[agentCards.length % AGENT_COLORS.length],
      content: formatResponseContent(finalEvent),
    });
  }

  const startTime = new Date(input.startedAt).toLocaleTimeString();
  const endRef = input.finishedAt ?? Date.now();
  const endTime = new Date(endRef).toLocaleTimeString();

  const timeline: TimelineStep[] = [
    { label: "Query received", time: startTime, active: true },
  ];
  if (routingPresent) {
    timeline.push({ label: "Routing decision", time: startTime, active: true });
  }
  for (const e of expertEvents) {
    timeline.push({
      label: agentLabel(e.capability),
      time: timeFromTrace(e.payload, input.startedAt),
      active: true,
    });
  }
  if (finalEvent) {
    timeline.push({
      label: "Synthesis",
      time: timeFromTrace(finalEvent, endRef),
      active: true,
    });
  }
  if (input.status === "running") {
    timeline.push({ label: "Streaming…", time: endTime, active: false });
  } else {
    timeline.push({
      label: input.status === "completed" ? "Run completed" : "Run failed",
      time: endTime,
      active: true,
    });
  }

  const agents = Array.from(new Set(expertEvents.map((e) => agentLabel(e.capability))));
  if (finalEvent) agents.push("Synthesis");

  const duration =
    input.status === "running"
      ? `${formatDuration(input.startedAt, Date.now())} (running)`
      : formatDuration(input.startedAt, input.finishedAt ?? Date.now());

  const runOverview: RunOverviewData = {
    runId: input.id,
    started: formatStarted(input.startedAt),
    duration,
    agents,
    timeline,
  };

  return { runOverview, agentCards };
}
