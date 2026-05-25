import { Fragment } from "react";
import { GitBranch } from "lucide-react";
import type { RoutingPayload } from "../../../api/events";
import type { AgentColor } from "../../../types";

const COLOR_BY_CAPABILITY: Record<string, AgentColor> = {
  cardiology:     "blue",
  research:       "green",
  pharmaceutical: "purple",
};

const PILL_CLASSES: Record<AgentColor, string> = {
  blue:   "bg-blue-50 text-blue-700 border-blue-200",
  green:  "bg-green-50 text-green-700 border-green-200",
  yellow: "bg-yellow-50 text-yellow-700 border-yellow-200",
  purple: "bg-purple-50 text-purple-700 border-purple-200",
};

interface RoutingPanelProps {
  payload: RoutingPayload;
}

export function RoutingPanel({ payload }: RoutingPanelProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 flex items-center gap-2 border-b border-gray-100">
        <GitBranch className="w-4 h-4 text-gray-500 flex-shrink-0" />
        <div className="font-medium text-sm text-gray-900">Routing</div>
      </div>

      <div className="px-4 py-3 grid grid-cols-[auto_1fr] gap-x-3 gap-y-2.5 items-start">
        {payload.assignments.map((a, i) => {
          const color = COLOR_BY_CAPABILITY[a.capability] ?? "yellow";
          return (
            <Fragment key={i}>
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded-full border text-xs font-medium justify-self-start ${PILL_CLASSES[color]}`}
              >
                {a.capability}
              </span>
              <p className="text-sm text-gray-800 leading-relaxed">{a.task}</p>
            </Fragment>
          );
        })}
      </div>

      <div className="px-4 py-3 border-t border-gray-100 bg-gray-50/50">
        <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
          Reasoning
        </div>
        <p className="text-xs text-gray-600 leading-relaxed">{payload.reasoning}</p>
      </div>
    </div>
  );
}
