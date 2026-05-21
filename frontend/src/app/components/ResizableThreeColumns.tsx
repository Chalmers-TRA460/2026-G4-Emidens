import { useRef, useState, type ReactNode } from "react";
import { PanelRightOpen } from "lucide-react";

const MIN_SIDE_PCT = 12;
const MIN_CENTER_PCT = 25;

interface ResizableThreeColumnsProps {
  left: ReactNode;
  center: ReactNode;
  right: ReactNode | null;
  initialLeftPct?: number;
  initialRightPct?: number;
  onExpandRight?: () => void;
}

export function ResizableThreeColumns({
  left,
  center,
  right,
  initialLeftPct = 20,
  initialRightPct = 35,
  onExpandRight,
}: ResizableThreeColumnsProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [leftPct, setLeftPct] = useState(initialLeftPct);
  const [rightPct, setRightPct] = useState(initialRightPct);

  const leftPctRef = useRef(leftPct);
  const rightPctRef = useRef(rightPct);
  leftPctRef.current = leftPct;
  rightPctRef.current = rightPct;

  const startDrag =
    (which: "left" | "right") => (e: React.PointerEvent<HTMLDivElement>) => {
      e.preventDefault();
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";

      const onMove = (ev: PointerEvent) => {
        const el = containerRef.current;
        if (!el) return;
        const rect = el.getBoundingClientRect();
        if (rect.width === 0) return;
        const xPct = ((ev.clientX - rect.left) / rect.width) * 100;

        if (which === "left") {
          const cap = 100 - (right ? rightPctRef.current : 0) - MIN_CENTER_PCT;
          const next = Math.max(MIN_SIDE_PCT, Math.min(cap, xPct));
          setLeftPct(next);
        } else {
          const cap = 100 - leftPctRef.current - MIN_CENTER_PCT;
          const next = Math.max(MIN_SIDE_PCT, Math.min(cap, 100 - xPct));
          setRightPct(next);
        }
      };

      const onUp = () => {
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
        window.removeEventListener("pointermove", onMove);
        window.removeEventListener("pointerup", onUp);
        window.removeEventListener("pointercancel", onUp);
      };

      window.addEventListener("pointermove", onMove);
      window.addEventListener("pointerup", onUp);
      window.addEventListener("pointercancel", onUp);
    };

  return (
    <div
      ref={containerRef}
      className="flex-1 flex overflow-hidden min-h-0 px-5 py-5 gap-0"
    >
      <div
        style={{ width: `${leftPct}%` }}
        className="flex flex-col min-w-0 overflow-hidden"
      >
        {left}
      </div>
      <ResizeHandle onPointerDown={startDrag("left")} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">{center}</div>
      {right ? (
        <>
          <ResizeHandle onPointerDown={startDrag("right")} />
          <div
            style={{ width: `${rightPct}%` }}
            className="flex flex-col min-w-0 overflow-hidden"
          >
            {right}
          </div>
        </>
      ) : onExpandRight ? (
        <ExpandTab onClick={onExpandRight} />
      ) : null}
    </div>
  );
}

function ResizeHandle({
  onPointerDown,
}: {
  onPointerDown: (e: React.PointerEvent<HTMLDivElement>) => void;
}) {
  return (
    <div
      role="separator"
      aria-orientation="vertical"
      onPointerDown={onPointerDown}
      className="group relative w-3 flex-shrink-0 cursor-col-resize"
    >
      <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-px bg-gray-200 group-hover:bg-blue-400 group-active:bg-blue-600 transition-colors" />
    </div>
  );
}

function ExpandTab({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      aria-label="Expand document panel"
      className="ml-2 flex flex-col items-center justify-center w-6 rounded-md border border-gray-200 bg-white text-gray-500 hover:text-blue-600 hover:border-blue-300 transition-colors"
    >
      <PanelRightOpen className="w-4 h-4" />
    </button>
  );
}
