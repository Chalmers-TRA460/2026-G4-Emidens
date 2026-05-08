import { FileText } from "lucide-react";

export function DocumentPlaceholder() {
  return (
    <div className="bg-white rounded-lg border border-gray-200 h-full flex flex-col">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900 text-sm">Document</h3>
      </div>
      <div className="flex-1 flex flex-col items-center justify-center text-gray-400 px-6 text-center">
        <FileText className="w-8 h-8 mb-2 text-gray-300" />
        <div className="text-sm font-medium text-gray-500">Placeholder</div>
        <div className="text-xs mt-1">
          Source document preview will appear here once attached.
        </div>
      </div>
    </div>
  );
}
