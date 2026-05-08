import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { clear, loadAll } from "../../storage/sessions";

export function SettingsPage() {
  const [count, setCount] = useState(0);

  const refresh = () => setCount(loadAll().length);

  useEffect(() => {
    refresh();
  }, []);

  const onClear = () => {
    const ok = window.confirm(
      `Clear ${count} stored session${count === 1 ? "" : "s"}? This cannot be undone.`,
    );
    if (!ok) return;
    clear();
    refresh();
  };

  return (
    <div className="flex-1 flex flex-col min-w-0">
      <div className="border-b border-gray-200 bg-white px-6 py-3.5">
        <h1 className="text-base font-semibold text-gray-900">Settings</h1>
      </div>

      <div className="flex-1 p-5 overflow-y-auto">
        <div className="max-w-2xl space-y-4">
          <section className="bg-white rounded-lg border border-gray-200 p-5">
            <h2 className="text-sm font-semibold text-gray-900">Local chat history</h2>
            <p className="text-xs text-gray-500 mt-1">
              Sessions are stored only in this browser's local storage. They are never synced.
            </p>
            <div className="mt-3 flex items-center justify-between">
              <span className="text-sm text-gray-700">
                {count} stored session{count === 1 ? "" : "s"}
              </span>
              <button
                onClick={onClear}
                disabled={count === 0}
                className="inline-flex items-center gap-1.5 text-xs text-red-600 hover:text-red-700 disabled:text-gray-400 disabled:cursor-not-allowed"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Clear history
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
