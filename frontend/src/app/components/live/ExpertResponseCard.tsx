import { AgentCard } from "../AgentCard";
import type { ResponsePayload } from "../../../api/events";
import type { AgentColor } from "../../../types";

const COLOR_BY_CAPABILITY: Record<string, AgentColor> = {
  cardiology:  "blue",
  research:    "green",
  regulatory:  "yellow",
  drug_dosing: "purple",
};

interface ExpertResponseCardProps {
  payload: ResponsePayload;
  isFinal?: boolean;
}

export function ExpertResponseCard({ payload, isFinal = false }: ExpertResponseCardProps) {
  const color = COLOR_BY_CAPABILITY[payload.capability] ?? "blue";
  const name = isFinal ? "Final Answer" : prettyCapability(payload.capability);
  const timestamp = `confidence ${payload.confidence.toFixed(2)}${payload.escalate ? " · escalate" : ""}`;

  return (
    <AgentCard agentName={name} timestamp={timestamp} color={color} defaultExpanded={true}>
      <div className="space-y-3 text-sm text-gray-800">
        <div className="whitespace-pre-wrap leading-relaxed">{payload.answer}</div>

        {payload.citations.length > 0 && (
          <div>
            <div className="font-medium text-gray-900 mb-1.5 text-xs uppercase tracking-wide">Citations</div>
            <ul className="space-y-1.5 text-xs text-gray-700">
              {payload.citations.map((c, i) => (
                <li key={i} className="border-l-2 border-gray-200 pl-2">
                  <div className="font-medium">{c.source}</div>
                  <div className="text-gray-600">{c.section}</div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {payload.trace.length > 0 && (
          <details className="text-xs text-gray-600">
            <summary className="cursor-pointer hover:text-gray-900">Trace ({payload.trace.length})</summary>
            <div className="mt-2 space-y-1 font-mono">
              {payload.trace.map((s, i) => (
                <div key={i}>
                  <span className="text-gray-400">[{s.time}]</span>{" "}
                  <span className="text-gray-500">[{s.agent}]</span>{" "}
                  <span>{s.message}</span>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </AgentCard>
  );
}

function prettyCapability(cap: string): string {
  return cap.split("_").map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join(" ");
}
