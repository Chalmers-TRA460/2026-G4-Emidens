import { GitBranch } from "lucide-react";
import type { RoutingPayload } from "../../../api/events";

interface RoutingPanelProps {
  payload: RoutingPayload;
}

export function RoutingPanel({ payload }: RoutingPanelProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center gap-2 mb-3">
        <GitBranch className="w-4 h-4 text-gray-500" />
        <div className="font-medium text-sm text-gray-900">Routing</div>
      </div>

      <div className="space-y-2 mb-3">
        {payload.assignments.map((a, i) => (
          <div key={i} className="flex gap-3 text-sm">
            <div className="font-medium text-blue-600 w-28 flex-shrink-0">{a.capability}</div>
            <div className="text-gray-700">{a.task}</div>
          </div>
        ))}
      </div>

      <div className="text-xs text-gray-500 leading-relaxed border-t border-gray-100 pt-2">
        {payload.reasoning}
      </div>
    </div>
  );
}
