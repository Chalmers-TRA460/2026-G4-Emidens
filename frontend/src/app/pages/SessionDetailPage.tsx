import { useState } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { Header } from '../components/Header';
import { RunOverview } from '../components/RunOverview';
import { SourcePreview } from '../components/SourcePreview';
import { AgentResponses } from '../components/AgentResponses';
import { mockAgentCards, sessions } from '../../mockData';

type TabId = 'responses' | 'conversation';

const tabs: { id: TabId; label: string }[] = [
  { id: 'responses', label: 'Agent Responses' },
  { id: 'conversation', label: 'Conversation' },
];

export function SessionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<TabId>('responses');

  const session = sessions.find((s) => s.id === id);

  if (!session) {
    return <Navigate to="/" replace />;
  }

  const run = session.run;

  return (
    <div className="flex-1 flex flex-col min-w-0">
      <Header
        breadcrumbs={[
          { label: 'Sessions', to: '/' },
          { label: session.label },
        ]}
        query={run.query}
        status={run.status}
        finishedAgo={run.finishedAgo}
      />

      <div className="flex-1 flex gap-5 p-5 overflow-hidden">
        <div className="w-64 flex-shrink-0 overflow-y-auto">
          <RunOverview data={run.overview} />
        </div>

        <div className="flex-1 flex flex-col min-w-0">
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
                          ? 'border-blue-500 text-blue-500 font-medium'
                          : 'border-transparent text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      {tab.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {activeTab === 'responses' ? (
                <AgentResponses agents={mockAgentCards} />
              ) : (
                <div className="py-8 text-center text-gray-500 text-sm">
                  Conversation view coming soon
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="w-[500px] flex-shrink-0 overflow-hidden">
          <SourcePreview data={run.source} />
        </div>
      </div>
    </div>
  );
}
