import {
  SSE_EVENTS,
  type StreamEvent,
  type ResponsePayload,
  type ToolResultPayload,
} from "../api/events";
import type { AgentCardData, AgentColor, RunOverviewData, TimelineStep } from "../types";
import { formatStarted, humanize } from "./format";

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
  toolResults: Map<string, ToolResultPayload>;
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
  return `${humanize(capability)} Expert`;
}

export function deriveSessionView(input: DeriveInput): DerivedSessionView {
  const latestByCapability = new Map<string, ResponsePayload>();
  const orderedCapabilities: string[] = [];
  const toolResults = new Map<string, ToolResultPayload>();
  let finalEvent: ResponsePayload | undefined;
  let routingPresent = false;

  for (const ev of input.events) {
    if (ev.type === SSE_EVENTS.ROUTING) {
      routingPresent = true;
    } else if (ev.type === SSE_EVENTS.EXPERT_RESPONSE) {
      const cap = ev.data.capability;
      if (!latestByCapability.has(cap)) orderedCapabilities.push(cap);
      latestByCapability.set(cap, ev.data);
    } else if (ev.type === SSE_EVENTS.FINAL) {
      finalEvent = ev.data;
    } else if (ev.type === SSE_EVENTS.TOOL_RESULT && ev.data.tool_call_id) {
      toolResults.set(ev.data.tool_call_id, ev.data);
    }
  }

  const expertEvents = orderedCapabilities.map((cap) => ({
    capability: cap,
    payload: latestByCapability.get(cap)!,
  }));

  const agentCards: AgentCardData[] = expertEvents.map((e, i) => ({
    agentName: agentLabel(e.capability),
    timestamp: timeFromTrace(e.payload, input.startedAt),
    color: AGENT_COLORS[i % AGENT_COLORS.length],
    content: e.payload.answer.trim(),
    citations: e.payload.citations,
    confidence: e.payload.confidence,
    isFinal: false,
  }));

  if (finalEvent) {
    agentCards.push({
      agentName: "Synthesis",
      timestamp: timeFromTrace(finalEvent, input.finishedAt ?? Date.now()),
      color: AGENT_COLORS[agentCards.length % AGENT_COLORS.length],
      content: finalEvent.answer.trim(),
      citations: finalEvent.citations,
      confidence: finalEvent.confidence,
      isFinal: true,
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

  const runOverview: RunOverviewData = {
    runId: input.id,
    started: formatStarted(input.startedAt),
    startedAt: input.startedAt,
    endedAt: input.status === "running" ? null : input.finishedAt ?? Date.now(),
    status: input.status,
    agents,
    timeline,
  };

  return { runOverview, agentCards, toolResults };
}
