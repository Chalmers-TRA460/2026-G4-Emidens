import { Calendar, Hash, Bot, Clock } from 'lucide-react';
import type { RunOverviewData } from '../../types';

interface RunOverviewProps {
  data: RunOverviewData;
}

export function RunOverview({ data }: RunOverviewProps) {
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-3 text-sm">Run Overview</h3>

        <div className="space-y-3">
          <div className="flex items-start gap-2">
            <Hash className="w-3.5 h-3.5 text-gray-400 mt-0.5" />
            <div>
              <div className="text-xs text-gray-500">Run ID</div>
              <div className="text-xs text-gray-900 font-mono">{data.runId}</div>
            </div>
          </div>

          <div className="flex items-start gap-2">
            <Calendar className="w-3.5 h-3.5 text-gray-400 mt-0.5" />
            <div>
              <div className="text-xs text-gray-500">Started</div>
              <div className="text-xs text-gray-900">{data.started}</div>
            </div>
          </div>

          <div className="flex items-start gap-2">
            <Clock className="w-3.5 h-3.5 text-gray-400 mt-0.5" />
            <div>
              <div className="text-xs text-gray-500">Duration</div>
              <div className="text-xs text-gray-900">{data.duration}</div>
            </div>
          </div>

          <div className="flex items-start gap-2">
            <Bot className="w-3.5 h-3.5 text-gray-400 mt-0.5" />
            <div>
              <div className="text-xs text-gray-500 mb-1">Agents Used</div>
              <div className="flex flex-wrap gap-1">
                {data.agents.map((agent) => (
                  <span
                    key={agent}
                    className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded border border-blue-200"
                  >
                    {agent}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-3 text-sm">Timeline</h3>

        <div className="space-y-2">
          {data.timeline.map((step, index) => (
            <div key={index} className="flex items-start gap-2">
              <div className="flex flex-col items-center">
                <div className={`w-1.5 h-1.5 rounded-full ${step.active ? 'bg-[#3b82f6]' : 'bg-gray-300'}`} />
                {index < data.timeline.length - 1 && (
                  <div className="w-px h-6 bg-gray-200 mt-1" />
                )}
              </div>
              <div className="flex-1 pb-1">
                <div className="text-xs text-gray-900">{step.label}</div>
                <div className="text-xs text-gray-500">{step.time}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
