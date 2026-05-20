import { AgentCard } from './AgentCard';
import { Markdown } from './Markdown';
import { CitationList } from './CitationList';
import type { AgentCardData } from '../../types';
import type { Citation } from '../../api/events';

interface AgentResponsesProps {
  agents:    AgentCardData[];
  selected?: Citation | null;
  onSelect?: (c: Citation) => void;
}

const noop = () => {};

export function AgentResponses({ agents, selected = null, onSelect = noop }: AgentResponsesProps) {
  return (
    <div className="space-y-3">
      {agents.map((agent, i) => (
        <AgentCard key={i} agentName={agent.agentName} timestamp={agent.timestamp} color={agent.color}>
          <Markdown>{agent.content}</Markdown>
          <CitationList
            citations={agent.citations}
            selected={selected}
            onSelect={onSelect}
          />
        </AgentCard>
      ))}
    </div>
  );
}
