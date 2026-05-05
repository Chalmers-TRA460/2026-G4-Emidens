import { RunPanel } from "../components/live/RunPanel";

export function AgentsPage() {
  return (
    <div className="flex-1 flex flex-col min-w-0 min-h-0">
      <div className="border-b border-gray-200 bg-white px-6 py-3.5">
        <h1 className="text-base font-semibold text-gray-900">Agents</h1>
        <p className="text-xs text-gray-500 mt-0.5">
          Direct expert interactions for development. Bypasses the orchestrator's routing,
          re-prompt loop, and synthesis.
        </p>
      </div>
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 min-h-0">
        <RunPanel
          title="Pharmaceutical (direct)"
          path="/dev/pharmaceutical/stream"
          badge="dev"
          placeholder="Drug query — bypasses orchestrator…"
        />
        <RunPanel
          title="Research (direct)"
          path="/dev/research/stream"
          badge="dev"
          placeholder="Evidence-grading query — bypasses orchestrator…"
        />
      </div>
    </div>
  );
}
