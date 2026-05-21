export const SSE_EVENTS = {
  ROUTING:         "routing",
  EXPERT_RESPONSE: "expert_response",
  FINAL:           "final",
  REASONING:       "reasoning",
  TOOL_CALL:       "tool_call",
  TOOL_RESULT:     "tool_result",
  DONE:            "done",
} as const;

export type SSEEventType = typeof SSE_EVENTS[keyof typeof SSE_EVENTS];

export interface Citation {
  source:        string;
  section:       string;
  tool_call_id?: string;
  confidence:    number;
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
  requested_inputs?: string[];
}

export interface RoutingAssignment {
  capability: string;
  task: string;
}

export interface RoutingPayload {
  assignments: RoutingAssignment[];
  reasoning: string;
}

export interface ReasoningPayload {
  text: string;
}

export interface GuidelineChunk {
  chunk_id:     string;
  doc_id:       number;
  heading_path: string;
  text:         string;
  score:        number;
}

export interface FassChunk {
  chunk_id:       string;
  doc_folder:     string;
  lakemedel:      string;
  substans?:      string | null;
  beredningsform: string;
  section:        string;
  atc_code:       string;
  content:        string;
  score:          number;
}

export interface PubMedAbstractSection {
  label: string | null;
  text:  string;
}

export interface PubMedItem {
  pmid:     string;
  title:    string;
  year:     number | null;
  journal:  string | null;
  authors:  string[];
  abstract: PubMedAbstractSection[];
  url:      string;
}

export type ToolArtifact =
  | { kind: "guidelines"; query: string; results: GuidelineChunk[] }
  | { kind: "fass";       query: string; results: FassChunk[] }
  | { kind: "drug_label"; drug_name: string; sections: Record<string, string> }
  | { kind: "pubmed";     query: string; results: PubMedItem[] };

export interface ToolCallPayload {
  tool: string;
  input: unknown;
  tool_call_id?: string;
}

export interface ToolResultPayload {
  tool: string;
  output: unknown;
  tool_call_id?: string;
  artifact?: ToolArtifact | null;
}

export type StreamEvent =
  | { type: typeof SSE_EVENTS.ROUTING;         data: RoutingPayload }
  | { type: typeof SSE_EVENTS.EXPERT_RESPONSE; data: ResponsePayload }
  | { type: typeof SSE_EVENTS.FINAL;           data: ResponsePayload }
  | { type: typeof SSE_EVENTS.REASONING;       data: ReasoningPayload }
  | { type: typeof SSE_EVENTS.TOOL_CALL;       data: ToolCallPayload }
  | { type: typeof SSE_EVENTS.TOOL_RESULT;     data: ToolResultPayload }
  | { type: typeof SSE_EVENTS.DONE;            data: Record<string, never> };
