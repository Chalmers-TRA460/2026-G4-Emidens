import { memo, useEffect, useState } from "react";
import { formatDuration } from "../../storage/format";

interface LiveDurationProps {
  startedAt: number;
  endedAt:   number | null;
  className?: string;
}

export const LiveDuration = memo(function LiveDuration({
  startedAt,
  endedAt,
  className,
}: LiveDurationProps) {
  const running = endedAt === null;
  const [now, setNow] = useState(() => (running ? Date.now() : endedAt));

  useEffect(() => {
    if (!running) {
      setNow(endedAt);
      return;
    }
    setNow(Date.now());
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, [running, endedAt]);

  const text = running
    ? `${formatDuration(startedAt, now)} (running)`
    : formatDuration(startedAt, now);

  return <span className={className}>{text}</span>;
});
