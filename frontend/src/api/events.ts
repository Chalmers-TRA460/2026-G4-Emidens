export const SSE_EVENTS = {
  ROUTING:         "routing",
  EXPERT_RESPONSE: "expert_response",
  FINAL:           "final",
  TOOL_CALL:       "tool_call",
  TOOL_RESULT:     "tool_result",
  DONE:            "done",
} as const;

export type SSEEventType = typeof SSE_EVENTS[keyof typeof SSE_EVENTS];

export interface Citation {
  source: string;
  section: string;
  location: string;
  confidence: number;
}

export interface TraceStep {
  agent: string;
  message: string;
  time: string;
}

export interface ResponsePayload {
  capability: string;
  answer: string;
  confidence: number;
  escalate: boolean;
  citations: Citation[];
  trace: TraceStep[];
}

export interface RoutingAssignment {
  capability: string;
  task: string;
}

export interface RoutingPayload {
  assignments: RoutingAssignment[];
  reasoning: string;
}

export interface ToolCallPayload {
  tool: string;
  input: unknown;
}

export interface ToolResultPayload {
  tool: string;
  output: unknown;
}

export type StreamEvent =
  | { type: typeof SSE_EVENTS.ROUTING;         data: RoutingPayload }
  | { type: typeof SSE_EVENTS.EXPERT_RESPONSE; data: ResponsePayload }
  | { type: typeof SSE_EVENTS.FINAL;           data: ResponsePayload }
  | { type: typeof SSE_EVENTS.TOOL_CALL;       data: ToolCallPayload }
  | { type: typeof SSE_EVENTS.TOOL_RESULT;     data: ToolResultPayload }
  | { type: typeof SSE_EVENTS.DONE;            data: Record<string, never> };
