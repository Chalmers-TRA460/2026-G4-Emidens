import { X } from 'lucide-react';
import type { Citation, ToolArtifact, ToolResultPayload } from '../../api/events';
import { formatConfidence, humanize } from '../../storage/format';
import { DocumentPlaceholder } from './DocumentPlaceholder';
import { Markdown } from './Markdown';

interface DocumentPanelProps {
  selected:    Citation | null;
  toolResults: Map<string, ToolResultPayload>;
  onClose:     () => void;
}

export function DocumentPanel({ selected, toolResults, onClose }: DocumentPanelProps) {
  if (!selected) return <DocumentPlaceholder />;
  const result = selected.tool_call_id ? toolResults.get(selected.tool_call_id) : undefined;

  return (
    <div className="bg-white rounded-lg border border-gray-200 h-full flex flex-col">
      <header className="px-4 py-3 border-b border-gray-200 flex items-start justify-between gap-2">
        <div className="min-w-0">
          <h3 className="font-semibold text-gray-900 text-sm truncate">{selected.source}</h3>
          <div className="text-xs text-gray-500 mt-0.5">
            confidence {formatConfidence(selected.confidence)}
          </div>
        </div>
        <button
          onClick={onClose}
          aria-label="Close preview"
          className="text-gray-400 hover:text-gray-700 shrink-0"
        >
          <X className="w-4 h-4" />
        </button>
      </header>
      <div className="flex-1 overflow-y-auto p-4">
        <ToolResultBody citation={selected} result={result} />
      </div>
    </div>
  );
}

interface MappedChunk {
  id:       string;
  title:    string;
  subtitle: string | null;
  score:    number;
  markdown: string;
}

function ToolResultBody({ citation, result }: { citation: Citation; result?: ToolResultPayload }) {
  if (result?.artifact) {
    return <ArtifactView artifact={result.artifact} />;
  }
  const fallback =
    typeof result?.output === 'string' ? result.output : citation.section;
  return <Markdown>{fallback || '_No preview available._'}</Markdown>;
}

function ArtifactView({ artifact }: { artifact: ToolArtifact }) {
  switch (artifact.kind) {
    case 'guidelines':
      return (
        <RetrievalView
          query={artifact.query}
          chunks={artifact.results.map((c) => ({
            id:       c.chunk_id,
            title:    c.heading_path || `Document ${c.doc_id}`,
            subtitle: null,
            score:    c.score,
            markdown: c.text,
          }))}
        />
      );
    case 'fass':
      return (
        <RetrievalView
          query={artifact.query}
          chunks={artifact.results.map((c) => ({
            id:       c.chunk_id,
            title:    `${c.lakemedel} — ${c.beredningsform}`,
            subtitle: `${c.section} · ATC ${c.atc_code}`,
            score:    c.score,
            markdown: c.content,
          }))}
        />
      );
    case 'drug_label':
      return <DrugLabelView drugName={artifact.drug_name} sections={artifact.sections} />;
    default:
      return null;
  }
}

function RetrievalView({ query, chunks }: { query: string; chunks: MappedChunk[] }) {
  if (chunks.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        <span className="font-medium">Query:</span> {query} · no results
      </div>
    );
  }
  return (
    <div className="space-y-4">
      <div className="text-xs text-gray-500">
        <span className="font-medium">Query:</span> {query} · {chunks.length} results
      </div>
      {chunks.map((c, i) => (
        <article key={c.id} className="border border-gray-200 rounded-md overflow-hidden">
          <header className="bg-gray-50 px-3 py-2 border-b border-gray-200 flex items-start justify-between gap-2">
            <div className="min-w-0">
              <div className="font-medium text-sm text-gray-900">{c.title}</div>
              {c.subtitle && (
                <div className="text-xs text-gray-500 mt-0.5">{c.subtitle}</div>
              )}
            </div>
            <span className="text-xs text-gray-500 shrink-0">
              #{i + 1} · {c.score.toFixed(2)}
            </span>
          </header>
          <div className="p-3">
            <Markdown>{c.markdown}</Markdown>
          </div>
        </article>
      ))}
    </div>
  );
}

function DrugLabelView({
  drugName,
  sections,
}: {
  drugName: string;
  sections: Record<string, string>;
}) {
  const entries = Object.entries(sections);
  if (entries.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        No label sections available for <span className="font-medium">{drugName}</span>.
      </div>
    );
  }
  const md = entries
    .map(([key, body]) => `## ${humanize(key)}\n\n${body}`)
    .join('\n\n');
  return (
    <div>
      <div className="text-xs text-gray-500 mb-2">
        <span className="font-medium">Drug:</span> {drugName}
      </div>
      <Markdown>{md}</Markdown>
    </div>
  );
}

