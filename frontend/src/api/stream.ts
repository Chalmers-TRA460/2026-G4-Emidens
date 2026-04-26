import type { StreamEvent } from "./events";

const DEFAULT_BASE_URL = "http://127.0.0.1:8080";

function getBaseUrl(): string {
  const fromEnv = import.meta.env.VITE_API_BASE_URL;
  if (typeof fromEnv === "string" && fromEnv.length > 0) return fromEnv;
  console.warn(`VITE_API_BASE_URL not set, falling back to ${DEFAULT_BASE_URL}`);
  return DEFAULT_BASE_URL;
}

export async function* streamQuery(
  query: string,
  signal?: AbortSignal,
): AsyncGenerator<StreamEvent> {
  const res = await fetch(`${getBaseUrl()}/query/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ query }),
    signal,
  });

  if (!res.ok || !res.body) {
    throw new Error(`stream request failed: ${res.status} ${res.statusText}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");

    let sep: number;
    while ((sep = buf.indexOf("\n\n")) !== -1) {
      const block = buf.slice(0, sep);
      buf = buf.slice(sep + 2);

      let event = "message";
      let data = "";
      for (const line of block.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data += line.slice(5).trim();
      }
      if (!data) continue;

      yield { type: event, data: JSON.parse(data) } as StreamEvent;
    }
  }
}
