import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, Navigate } from 'react-router-dom';
import { Header } from '../components/Header';
import { RunOverview } from '../components/RunOverview';
import { SourcePreview } from '../components/SourcePreview';
import { AgentResponses } from '../components/AgentResponses';
import { RichRunView } from '../components/RichRunView';
import { QueryInput } from '../components/live/QueryInput';
import { ClinicalInputForm } from '../components/live/ClinicalInputForm';
import { mockAgentCards, sessions } from '../../mockData';
import { get as getStoredSession, type StoredSession } from '../../storage/sessions';
import { relativeTime } from '../../storage/format';
import { deriveSessionView, type DeriveStatus } from '../../storage/derive';
import { useActiveRun } from '../ActiveRunContext';
import { SSE_EVENTS } from '../../api/events';
import type { ClinicalContext } from '../../api/stream';

type TabId = 'responses' | 'conversation';

const tabs: { id: TabId; label: string }[] = [
  { id: 'responses', label: 'Agent Responses' },
  { id: 'conversation', label: 'Conversation' },
];

const STATUS_LABEL: Record<string, string> = {
  idle:      'Ready',
  streaming: 'Streaming…',
  done:      'Done',
  error:     'Error',
};

const STATUS_COLOR: Record<string, string> = {
  idle:      'bg-gray-100 text-gray-600',
  streaming: 'bg-blue-100 text-blue-700',
  done:      'bg-green-100 text-green-700',
  error:     'bg-red-100 text-red-700',
};

function deriveStatusOf(s: 'idle' | 'streaming' | 'done' | 'error'): DeriveStatus {
  if (s === 'done') return 'completed';
  if (s === 'error') return 'failed';
  return 'running';
}

export function SessionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<TabId>('responses');
  const [stored, setStored] = useState<StoredSession | undefined>(undefined);
  const [storedLoaded, setStoredLoaded] = useState(false);

  const activeRun = useActiveRun();
  const isLive = !!id && activeRun.runId === id;

  useEffect(() => {
    if (isLive) {
      setStoredLoaded(true);
      return;
    }
    setStored(id ? getStoredSession(id) : undefined);
    setStoredLoaded(true);
  }, [id, isLive, activeRun.status]);

  if (isLive) {
    return <LiveSessionView />;
  }

  if (stored) {
    return <StoredSessionView session={stored} />;
  }

  const mockSession = sessions.find((s) => s.id === id);
  if (mockSession) {
    return (
      <MockSessionView
        session={mockSession}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />
    );
  }

  if (!storedLoaded) return null;
  return <Navigate to="/sessions" replace />;
}

function LiveSessionView() {
  const navigate = useNavigate();
  const { events, status, error, runId, query, startedAt, submit, reset } = useActiveRun();

  const derived = useMemo(() => {
    if (!runId || !startedAt) return null;
    return deriveSessionView({
      id: runId,
      startedAt,
      finishedAt: status === 'done' || status === 'error' ? Date.now() : null,
      status: deriveStatusOf(status),
      events,
    });
  }, [runId, startedAt, status, events]);

  const requestedInputs = useMemo(() => {
    const seen = new Set<string>();
    const ordered: string[] = [];
    for (const ev of events) {
      if (ev.type !== SSE_EVENTS.FINAL && ev.type !== SSE_EVENTS.EXPERT_RESPONSE) continue;
      for (const f of ev.data.requested_inputs ?? []) {
        if (!seen.has(f)) {
          seen.add(f);
          ordered.push(f);
        }
      }
    }
    return ordered;
  }, [events]);

  const showInputForm =
    requestedInputs.length > 0 && status !== 'streaming' && query !== null;

  const handleAnswerInputs = (ctx: ClinicalContext, skippedFields?: string[]) => {
    if (!query || !runId) return;
    submit(query, ctx, skippedFields, runId);
  };

  const handleFollowUp = (nextQuery: string) => {
    const id = submit(nextQuery);
    navigate(`/sessions/${id}`);
  };

  const handleClear = () => {
    reset();
    navigate('/new');
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 min-h-0">
      <div className="border-b border-gray-200 bg-white px-6 py-3.5 flex items-center justify-between gap-4 min-w-0">
        <h1
          className="text-base font-semibold text-gray-900 truncate"
          title={query ?? undefined}
        >
          {query ?? 'New Query'}
        </h1>
        <div className="flex items-center gap-3 shrink-0">
          <span className={`inline-flex px-2.5 py-0.5 rounded-full text-xs ${STATUS_COLOR[status]}`}>
            {STATUS_LABEL[status]}
          </span>
          <button
            onClick={handleClear}
            className="text-xs text-gray-500 hover:text-gray-900"
          >
            Clear
          </button>
        </div>
      </div>

      {showInputForm && (
        <div className="px-6 pt-4">
          <ClinicalInputForm
            fields={requestedInputs}
            onSubmit={handleAnswerInputs}
          />
        </div>
      )}

      {error && (
        <div className="mx-6 mt-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg p-3">
          {error.message}
        </div>
      )}

      {derived && (
        <RichRunView
          runOverview={derived.runOverview}
          agentCards={derived.agentCards}
          events={events}
          toolResults={derived.toolResults}
        />
      )}

      {status !== 'streaming' && !showInputForm && (
        <div className="border-t border-gray-200 bg-white px-6 py-2">
          <div className="max-w-3xl mx-auto">
            <QueryInput onSubmit={handleFollowUp} disabled={false} />
          </div>
        </div>
      )}
    </div>
  );
}

function StoredSessionView({ session }: { session: StoredSession }) {
  const status = session.status === 'completed' ? 'completed' : 'failed';
  const { runOverview, agentCards, toolResults } = deriveSessionView({
    id: session.id,
    startedAt: session.startedAt,
    finishedAt: session.finishedAt,
    status: session.status,
    events: session.events,
  });

  return (
    <div className="flex-1 flex flex-col min-w-0">
      <Header
        breadcrumbs={[
          { label: 'Sessions', to: '/sessions' },
          { label: relativeTime(session.startedAt) },
        ]}
        query={session.query}
        status={status}
        finishedAgo={relativeTime(session.finishedAt)}
      />
      <RichRunView
        runOverview={runOverview}
        agentCards={agentCards}
        events={session.events}
        toolResults={toolResults}
      />
    </div>
  );
}

function MockSessionView({
  session,
  activeTab,
  setActiveTab,
}: {
  session: typeof sessions[number];
  activeTab: TabId;
  setActiveTab: (id: TabId) => void;
}) {
  const run = session.run;
  return (
    <div className="flex-1 flex flex-col min-w-0">
      <Header
        breadcrumbs={[
          { label: 'Sessions', to: '/sessions' },
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
