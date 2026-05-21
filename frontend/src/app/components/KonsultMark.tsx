import { ECG_NODES, ECG_POINTS } from "./ecgGeometry";

interface KonsultMarkProps {
  className?: string;
}

export function KonsultMark({ className }: KonsultMarkProps) {
  return (
    <svg
      viewBox="0 0 32 32"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      className={className}
    >
      <polyline
        points={ECG_POINTS}
        stroke="currentColor"
        strokeWidth="1.6"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity="0.55"
      />
      {ECG_NODES.map(([cx, cy], i) => (
        <circle key={i} cx={cx} cy={cy} r="1.9" fill="currentColor" />
      ))}
    </svg>
  );
}
