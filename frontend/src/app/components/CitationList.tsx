import { FileText } from 'lucide-react';
import type { Citation } from '../../api/events';

interface Props {
  citations: Citation[];
  selected:  Citation | null;
  onSelect:  (c: Citation) => void;
}

export function CitationList({ citations, selected, onSelect }: Props) {
  if (citations.length === 0) return null;
  return (
    <div className="mt-3 pt-3 border-t border-gray-100">
      <div className="text-xs font-medium text-gray-500 mb-2">Citations</div>
      <div className="flex flex-wrap gap-1.5">
        {citations.map((c, i) => {
          const isActive =
            !!c.tool_call_id && c.tool_call_id === selected?.tool_call_id;
          return (
            <button
              key={c.tool_call_id ?? `${c.source}-${i}`}
              onClick={() => onSelect(c)}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs border transition-colors ${
                isActive
                  ? 'bg-blue-50 border-blue-300 text-blue-700'
                  : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
              }`}
            >
              <FileText className="w-3 h-3" />
              {c.source}
              <span className="text-gray-400">#{i + 1}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
