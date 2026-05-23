import { ECG_NODES } from "./ecgGeometry";

const BASELINE_Y = 18;
const FLATLINE_POINTS = ECG_NODES.map(([x]) => `${x},${BASELINE_Y}`).join(" ");

interface RunFailedProps {
  label?: string;
}

export function RunFailed({ label = "Run failed" }: RunFailedProps) {
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
        className="w-16 h-16 text-red-400"
      >
        <polyline
          points={FLATLINE_POINTS}
          stroke="currentColor"
          strokeWidth="1.6"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.55"
        />
        {ECG_NODES.map(([x], i) => (
          <circle key={i} cx={x} cy={BASELINE_Y} r="1.9" fill="currentColor" />
        ))}
      </svg>
      <div className="mt-4 text-sm text-red-700">{label}</div>
    </div>
  );
}
