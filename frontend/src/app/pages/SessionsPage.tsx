import { Link } from 'react-router-dom';
import { Clock } from 'lucide-react';
import { mockRun } from '../../mockData';
import { statusStyles } from '../../statusStyles';
import type { SessionRun } from '../../types';

// TODO: replace with data fetched from the backend
export const sessions: { id: string; label: string; run: SessionRun }[] = [
  { id: 'mock-run', label: 'Mock Run', run: mockRun },
];

export function SessionsPage() {
  return (
    <div className="flex-1 flex flex-col min-w-0">
      <div className="border-b border-gray-200 bg-white px-6 py-3.5">
        <h1 className="text-base font-semibold text-gray-900">Sessions</h1>
      </div>

      <div className="flex-1 p-5 overflow-y-auto">
        <div className="space-y-2">
          {sessions.map((session) => (
            <Link
              key={session.id}
              to={`/sessions/${session.id}`}
              className="block bg-white rounded-lg border border-gray-200 p-4 hover:border-[#3b82f6] hover:shadow-sm transition-all"
            >
              <div className="flex items-center gap-3">
                <Clock className="w-4 h-4 text-gray-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm text-gray-900">{session.label}</div>
                  <div className="text-xs text-gray-500 truncate mt-0.5">{session.run.query}</div>
                </div>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border ${statusStyles[session.run.status]}`}>
                  {session.run.statusLabel}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
