import { AgentCard } from './AgentCard';
import type { AgentCardData } from '../../types';

interface AgentResponsesProps {
  agents: AgentCardData[];
}

export function AgentResponses({ agents }: AgentResponsesProps) {
  return (
    <div className="space-y-3">
      {agents.map((agent, i) => (
        <AgentCard key={i} agentName={agent.agentName} timestamp={agent.timestamp} color={agent.color}>
          {agent.content}
        </AgentCard>
      ))}
    </div>
  );
}
