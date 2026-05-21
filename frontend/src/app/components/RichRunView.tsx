import { useEffect, useState } from "react";
import type { Citation, StreamEvent, ToolResultPayload } from "../../api/events";
import type { AgentCardData, RunOverviewData } from "../../types";
import { AgentResponses } from "./AgentResponses";
import { RunOverview } from "./RunOverview";
import { EventView } from "./live/EventView";
import { DocumentPanel } from "./DocumentPanel";
import { ResizableThreeColumns } from "./ResizableThreeColumns";
import { WaitingPulse } from "./WaitingPulse";

type TabId = "responses" | "conversation";

const tabs: { id: TabId; label: string }[] = [
  { id: "responses", label: "Agent Responses" },
  { id: "conversation", label: "Conversation" },
];

interface RichRunViewProps {
  runOverview: RunOverviewData;
  agentCards: AgentCardData[];
  events: StreamEvent[];
  toolResults: Map<string, ToolResultPayload>;
}

export function RichRunView({
  runOverview,
  agentCards,
  events,
  toolResults,
}: RichRunViewProps) {
  const [activeTab, setActiveTab] = useState<TabId>("responses");
  const [selected, setSelected] = useState<Citation | null>(null);
  const [docCollapsed, setDocCollapsed] = useState(true);

  useEffect(() => setSelected(null), [runOverview.runId]);

  const handleSelectCitation = (c: Citation) => {
    setSelected(c);
    setDocCollapsed(false);
  };

  return (
    <ResizableThreeColumns
      left={
        <div className="overflow-y-auto h-full">
          <RunOverview data={runOverview} />
        </div>
      }
      center={
        <div className="bg-white rounded-lg border border-gray-200 flex flex-col flex-1 overflow-hidden">
          <div className="border-b border-gray-200 px-4">
            <div className="flex gap-6">
              {tabs.map((tab) => {
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-3 px-1 border-b-2 transition-colors text-sm ${
                      isActive
                        ? "border-blue-500 text-blue-500 font-medium"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {activeTab === "responses" ? (
              <>
                {agentCards.length > 0 && (
                  <AgentResponses
                    agents={agentCards}
                    selected={selected}
                    onSelect={handleSelectCitation}
                  />
                )}
                {!agentCards.some((c) => c.isFinal) && <WaitingPulse />}
              </>
            ) : (
              <ConversationStream events={events} />
            )}
          </div>
        </div>
      }
      right={
        docCollapsed ? null : (
          <DocumentPanel
            selected={selected}
            toolResults={toolResults}
            onClose={() => setSelected(null)}
            onCollapse={() => setDocCollapsed(true)}
          />
        )
      }
      onExpandRight={() => setDocCollapsed(false)}
    />
  );
}

function ConversationStream({ events }: { events: StreamEvent[] }) {
  if (events.length === 0) {
    return (
      <div className="py-8 text-center text-gray-400 text-sm">
        No events yet.
      </div>
    );
  }
  return (
    <div className="space-y-3">
      {events.map((ev, i) => (
        <div key={i} className="animate-fade-up">
          <EventView event={ev} />
        </div>
      ))}
    </div>
  );
}
