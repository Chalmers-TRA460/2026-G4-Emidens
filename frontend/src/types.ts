export type RunStatus = 'running' | 'completed' | 'failed';

export type AgentColor = 'blue' | 'green' | 'yellow' | 'purple';

export interface TimelineStep {
  label: string;
  time: string;
  active: boolean;
}

export interface RunOverviewData {
  runId: string;
  started: string;
  duration: string;
  agents: string[];
  timeline: TimelineStep[];
}

export interface AgentCardData {
  agentName: string;
  timestamp: string;
  color: AgentColor;
  content: React.ReactNode;
}

export interface SourceData {
  title: string;
  journal: string;
  year: string;
  volume: string;
  page: string;
  sections: SourceSection[];
}

export interface SourceSection {
  type: "heading" | "paragraph" | "table";
  text?: string;
  highlights?: string[];
  table?: SourceTable;
}

export interface SourceTable {
  caption: string;
  headers: string[];
  rows: SourceTableRow[];
}

export interface SourceTableRow {
  cells: string[];
  highlighted?: boolean;
}

export interface SessionRun {
  id: string;
  query: string;
  status: RunStatus;
  finishedAgo: string;
  overview: RunOverviewData;
  source: SourceData | null;
}
