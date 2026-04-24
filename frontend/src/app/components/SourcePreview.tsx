import type { SourceData } from '../../types';

interface SourcePreviewProps {
  data: SourceData | null;
}

export function SourcePreview({ data }: SourcePreviewProps) {
  if (!data) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 h-full flex items-center justify-center text-gray-400 text-sm">
        No source selected
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 h-full flex flex-col">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900 text-sm">Source Preview</h3>
      </div>

      <div className="flex-1 overflow-auto p-4">
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
            <div className="font-medium text-gray-900 text-sm mb-1">{data.title}</div>
            <div className="text-xs text-gray-600">
              {data.journal} &bull; {data.year} &bull; {data.volume} &bull; {data.page}
            </div>
          </div>

          <div className="p-6 space-y-4 text-sm leading-relaxed text-gray-800">
            {data.sections.map((section, i) => {
              if (section.type === 'heading') {
                return <div key={i} className="font-semibold mb-2">{section.text}</div>;
              }

              if (section.type === 'table' && section.table) {
                const t = section.table;
                return (
                  <div key={i} className="my-4 border border-gray-300 rounded-md overflow-hidden">
                    <div className="bg-gray-100 px-3 py-2 border-b border-gray-300">
                      <div className="font-semibold text-xs">{t.caption}</div>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs">
                        <thead className="bg-gray-50 border-b border-gray-300">
                          <tr>
                            {t.headers.map((h, j) => (
                              <th key={j} className={`px-3 py-2 font-medium ${j === 0 ? 'text-left' : 'text-center'}`}>{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {t.rows.map((row, j) => (
                            <tr key={j} className={row.highlighted ? 'bg-yellow-50' : ''}>
                              {row.cells.map((cell, k) => (
                                <td key={k} className={`px-3 py-2 ${k === 0 ? '' : 'text-center'}`}>{cell}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                );
              }

              return <p key={i}>{section.text}</p>;
            })}
          </div>
        </div>
      </div>

      <div className="px-4 py-3 border-t border-gray-200">
        <button className="w-full py-2.5 bg-[#3b82f6] hover:bg-[#2563eb] text-white rounded-md text-sm font-medium transition-colors">
          Show exact place in text
        </button>
      </div>
    </div>
  );
}
