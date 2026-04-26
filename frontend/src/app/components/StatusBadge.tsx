import { statusLabels, statusStyles } from '../../statusStyles';
import type { RunStatus } from '../../types';

interface StatusBadgeProps {
  status: RunStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border ${statusStyles[status]}`}>
      {statusLabels[status]}
    </span>
  );
}
