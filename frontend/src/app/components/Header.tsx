import { ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { statusStyles } from '../../statusStyles';

interface Breadcrumb {
  label: string;
  to?: string;
}

interface HeaderProps {
  breadcrumbs: Breadcrumb[];
  query: string;
  status: 'running' | 'completed' | 'failed';
  statusLabel: string;
  finishedAgo: string;
}

export function Header({ breadcrumbs, query, status, statusLabel, finishedAgo }: HeaderProps) {
  return (
    <div className="border-b border-gray-200 bg-white">
      <div className="px-6 py-3.5">
        <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
          {breadcrumbs.map((crumb, i) => (
            <span key={i} className="flex items-center gap-2">
              {i > 0 && <ChevronRight className="w-3.5 h-3.5" />}
              {crumb.to ? (
                <Link to={crumb.to} className="hover:text-gray-900 cursor-pointer">
                  {crumb.label}
                </Link>
              ) : (
                <span className="text-gray-900">{crumb.label}</span>
              )}
            </span>
          ))}
        </div>

        <h1 className="text-base text-gray-900 mb-2">{query}</h1>
        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border ${statusStyles[status]}`}>
            {statusLabel}
          </span>
          <span className="text-xs text-gray-500">Finished {finishedAgo}</span>
        </div>
      </div>
    </div>
  );
}
