import type { ComponentType, ReactNode } from 'react';
import { Calendar, Hash, Bot, Clock } from 'lucide-react';
import type { RunOverviewData } from '../../types';

interface RunOverviewProps {
  data: RunOverviewData;
}

interface MetaRowProps {
  icon: ComponentType<{ className?: string }>;
  label: string;
  children: ReactNode;
}

function MetaRow({ icon: Icon, label, children }: MetaRowProps) {
  return (
    <div className="flex items-start gap-2">
      <Icon className="w-3.5 h-3.5 text-gray-400 mt-0.5" />
      <div>
        <div className="text-xs text-gray-500 mb-1">{label}</div>
        {children}
      </div>
    </div>
  );
}

export function RunOverview({ data }: RunOverviewProps) {
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-3 text-sm">Run Overview</h3>

        <div className="space-y-3">
          <MetaRow icon={Hash} label="Run ID">
            <div className="text-xs text-gray-900 font-mono">{data.runId}</div>
          </MetaRow>
          <MetaRow icon={Calendar} label="Started">
            <div className="text-xs text-gray-900">{data.started}</div>
          </MetaRow>
          <MetaRow icon={Clock} label="Duration">
            <div className="text-xs text-gray-900">{data.duration}</div>
          </MetaRow>
          <MetaRow icon={Bot} label="Agents Used">
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
          </MetaRow>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-3 text-sm">Timeline</h3>

        <div className="space-y-2">
          {data.timeline.map((step, index) => (
            <div key={index} className="flex items-start gap-2">
              <div className="flex flex-col items-center">
                <div className={`w-1.5 h-1.5 rounded-full ${step.active ? 'bg-blue-500' : 'bg-gray-300'}`} />
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
