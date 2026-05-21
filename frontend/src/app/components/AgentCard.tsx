import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import type { AgentColor } from '../../types';
import { formatConfidence } from '../../storage/format';

const colorClasses: Record<AgentColor, { border: string; icon: string }> = {
  blue: { border: 'border-blue-200', icon: 'bg-blue-500' },
  green: { border: 'border-green-200', icon: 'bg-green-500' },
  yellow: { border: 'border-yellow-200', icon: 'bg-yellow-500' },
  purple: { border: 'border-purple-200', icon: 'bg-purple-500' },
};

interface AgentCardProps {
  agentName: string;
  timestamp: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  color: AgentColor;
  confidence?: number;
}

function confidenceClasses(value: number): string {
  if (value >= 0.8) return 'bg-green-50 text-green-700 border-green-200';
  if (value >= 0.6) return 'bg-yellow-50 text-yellow-700 border-yellow-200';
  return 'bg-red-50 text-red-700 border-red-200';
}

export function AgentCard({ agentName, timestamp, children, defaultExpanded = true, color, confidence }: AgentCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const colors = colorClasses[color];

  return (
    <div className={`bg-white rounded-lg border ${colors.border} overflow-hidden`}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center gap-3 hover:bg-gray-50 transition-colors"
      >
        <div className={`w-2 h-2 rounded-full ${colors.icon} flex-shrink-0`} />
        <div className="flex-1 text-left min-w-0">
          <div className="font-medium text-gray-900 text-sm">{agentName}</div>
          <div className="text-xs text-gray-500">{timestamp}</div>
        </div>
        {confidence !== undefined && (
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded-full border text-xs font-medium ${confidenceClasses(confidence)}`}
          >
            {formatConfidence(confidence)}
          </span>
        )}
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
        )}
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 pt-2">
          {children}
        </div>
      )}
    </div>
  );
}
