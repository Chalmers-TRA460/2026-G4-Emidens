import { memo } from "react";
import { ECG_NODES, ECG_POINTS } from "./ecgGeometry";

interface WaitingPulseProps {
  label?: string;
}

export const WaitingPulse = memo(function WaitingPulse({
  label = "Consulting experts…",
}: WaitingPulseProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="py-8 flex flex-col items-center"
    >
      <svg
        viewBox="0 0 32 32"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        className="w-16 h-16 text-[#2546d9]"
      >
        <polyline
          points={ECG_POINTS}
          stroke="currentColor"
          strokeWidth="1.6"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.15"
        />
        <polyline
          pathLength={50}
          points={ECG_POINTS}
          stroke="currentColor"
          strokeWidth="1.6"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="ecg-trace"
        />
        {ECG_NODES.map(([cx, cy], i) => (
          <circle key={i} cx={cx} cy={cy} r="1.9" fill="currentColor" opacity="0.3" />
        ))}
      </svg>
      <div className="mt-4 text-sm text-gray-400">{label}</div>
    </div>
  );
});
