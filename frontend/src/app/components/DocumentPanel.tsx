import { X, PanelRightClose, ExternalLink } from 'lucide-react';
import type {
  Citation,
  PubMedItem,
  ToolArtifact,
  ToolResultPayload,
} from '../../api/events';
import { formatConfidence, humanize } from '../../storage/format';
import { DocumentPlaceholder } from './DocumentPlaceholder';
import { Markdown } from './Markdown';

interface DocumentPanelProps {
  selected:    Citation | null;
  toolResults: Map<string, ToolResultPayload>;
  onClose:     () => void;
  onCollapse:  () => void;
}

export function DocumentPanel({ selected, toolResults, onClose, onCollapse }: DocumentPanelProps) {
  if (!selected) return <DocumentPlaceholder onCollapse={onCollapse} />;
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
        <div className="flex items-center gap-1 shrink-0">
          <button
            onClick={onClose}
            aria-label="Close preview"
            className="p-1 text-gray-400 hover:text-gray-700"
          >
            <X className="w-4 h-4" />
          </button>
          <button
            onClick={onCollapse}
            aria-label="Collapse document panel"
            className="p-1 text-gray-400 hover:text-gray-700"
          >
            <PanelRightClose className="w-4 h-4" />
          </button>
        </div>
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
    case 'pubmed':
      return <PubMedView query={artifact.query} results={artifact.results} />;
    default:
      return null;
  }
}

function PubMedView({ query, results }: { query: string; results: PubMedItem[] }) {
  if (results.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        <span className="font-medium">PubMed:</span> {query} · no results
      </div>
    );
  }
  return (
    <div className="space-y-4">
      <div className="text-xs text-gray-500">
        <span className="font-medium">PubMed:</span> {query} · {results.length} results
      </div>
      {results.map((item, i) => (
        <article key={item.pmid} className="border border-gray-200 rounded-md overflow-hidden">
          <header className="bg-gray-50 px-3 py-2 border-b border-gray-200">
            <div className="flex items-start justify-between gap-2">
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-sm text-gray-900 hover:text-blue-600 inline-flex items-start gap-1 min-w-0"
              >
                {item.title}
                <ExternalLink className="w-3 h-3 mt-1 shrink-0 opacity-60" />
              </a>
              <span className="text-xs text-gray-500 shrink-0">#{i + 1}</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">
              PMID {item.pmid}
              {item.year !== null && ` · ${item.year}`}
              {item.journal && ` · ${item.journal}`}
            </div>
            {item.authors.length > 0 && (
              <div className="text-xs text-gray-500 mt-0.5 truncate">
                {item.authors.slice(0, 6).join(', ')}
                {item.authors.length > 6 ? ', et al.' : ''}
              </div>
            )}
          </header>
          <div className="p-3 text-sm text-gray-800">
            {item.abstract.length === 0 ? (
              <span className="text-gray-400 italic">No abstract available.</span>
            ) : (
              <div className="space-y-2">
                {item.abstract.map((s, j) => (
                  <p key={j}>
                    {s.label && (
                      <span className="font-medium text-gray-900">{s.label}: </span>
                    )}
                    {s.text}
                  </p>
                ))}
              </div>
            )}
          </div>
        </article>
      ))}
    </div>
  );
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

