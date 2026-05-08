import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Clock } from "lucide-react";
import { sessions as mockSessions } from "../../mockData";
import { StatusBadge } from "../components/StatusBadge";
import { loadAll, type StoredSession } from "../../storage/sessions";
import { relativeTime } from "../../storage/format";
import type { RunStatus } from "../../types";

interface SessionListItem {
  id: string;
  label: string;
  query: string;
  status: RunStatus;
  to: string;
}

function storedToItem(session: StoredSession): SessionListItem {
  return {
    id: session.id,
    label: relativeTime(session.startedAt),
    query: session.query,
    status: session.status === "completed" ? "completed" : "failed",
    to: `/sessions/${session.id}`,
  };
}

export function SessionsPage() {
  const [stored, setStored] = useState<StoredSession[]>([]);

  useEffect(() => {
    setStored(loadAll());
  }, []);

  const mockItems: SessionListItem[] = mockSessions.map((s) => ({
    id: s.id,
    label: s.label,
    query: s.run.query,
    status: s.run.status,
    to: `/sessions/${s.id}`,
  }));

  const items: SessionListItem[] = [...stored.map(storedToItem), ...mockItems];

  return (
    <div className="flex-1 flex flex-col min-w-0">
      <div className="border-b border-gray-200 bg-white px-6 py-3.5">
        <h1 className="text-base font-semibold text-gray-900">Sessions</h1>
      </div>

      <div className="flex-1 p-5 overflow-y-auto">
        {items.length === 0 ? (
          <div className="text-sm text-gray-500">
            No sessions yet. Start a query from{" "}
            <Link to="/new" className="text-blue-600 hover:underline">
              New Chat
            </Link>
            .
          </div>
        ) : (
          <div className="space-y-2">
            {items.map((item) => (
              <Link
                key={item.id}
                to={item.to}
                className="block bg-white rounded-lg border border-gray-200 p-4 hover:border-blue-500 hover:shadow-sm transition-all"
              >
                <div className="flex items-center gap-3">
                  <Clock className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm text-gray-900">{item.label}</div>
                    <div className="text-xs text-gray-500 truncate mt-0.5">{item.query}</div>
                  </div>
                  <StatusBadge status={item.status} />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
