import { useRef, useState, type FormEvent } from "react";
import { ArrowUp } from "lucide-react";
import { KonsultMark } from "../KonsultMark";

const MAX_HEIGHT_PX = 240;

const SUGGESTIONS: { label: string; query: string }[] = [
  { label: "Anticoagulation in AF",       query: "Anticoagulation for atrial fibrillation with CHA₂DS₂-VASc ≥2" },
  { label: "Beta-blocker in HFrEF",       query: "Metoprolol dosing in heart failure with reduced ejection fraction" },
  { label: "Drug interactions",           query: "Apixaban and amiodarone — interaction concerns" },
  { label: "Renal dose adjustment",       query: "Dose adjustment for cardiovascular drugs in CKD stage 4" },
];

interface WelcomeViewProps {
  onSubmit: (query: string) => void;
}

export function WelcomeView({ onSubmit }: WelcomeViewProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const resize = () => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, MAX_HEIGHT_PX)}px`;
  };

  const send = (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    send(value);
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 py-10 overflow-y-auto">
      <div className="w-full max-w-2xl">
        <div className="flex items-center justify-center gap-3 mb-10 text-[#2546d9]">
          <KonsultMark className="w-9 h-9" />
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">
            Good {timeOfDay()}, doctor
          </h1>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl border border-gray-200 shadow-sm px-5 pt-4 pb-3 focus-within:border-blue-300 focus-within:shadow-md transition-all"
        >
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => {
              setValue(e.target.value);
              resize();
            }}
            placeholder="Ask a clinical question…"
            rows={2}
            className="w-full resize-none bg-transparent text-base text-gray-900 placeholder:text-gray-400 focus:outline-none leading-7"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(value);
              }
            }}
          />
          <div className="flex items-center justify-between pt-2">
            <span className="text-xs text-gray-400">
              Press <kbd className="px-1.5 py-0.5 rounded border border-gray-200 bg-gray-50 font-mono text-[10px]">↵</kbd> to send
            </span>
            <button
              type="submit"
              aria-label="Send"
              disabled={!value.trim()}
              className="flex items-center justify-center w-9 h-9 rounded-full bg-[#2546d9] text-white hover:bg-blue-700 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors shadow-sm"
            >
              <ArrowUp className="w-4 h-4" />
            </button>
          </div>
        </form>

        <div className="flex flex-wrap gap-2 mt-5 justify-center">
          {SUGGESTIONS.map((s) => (
            <button
              key={s.label}
              onClick={() => send(s.query)}
              className="px-3.5 py-1.5 rounded-full border border-gray-200 bg-white text-xs text-gray-700 hover:border-blue-300 hover:text-blue-700 hover:bg-blue-50 transition-colors"
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function timeOfDay(): string {
  const h = new Date().getHours();
  if (h >= 5 && h < 12) return "morning";
  if (h >= 12 && h < 18) return "afternoon";
  return "evening";
}

