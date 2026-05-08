import { SSE_EVENTS, type StreamEvent } from "../../../api/events";
import { RoutingPanel } from "./RoutingPanel";
import { ToolEventLine } from "./ToolEventLine";
import { ReasoningLine } from "./ReasoningLine";
import { ExpertResponseCard } from "./ExpertResponseCard";

export function EventView({ event }: { event: StreamEvent }) {
  switch (event.type) {
    case SSE_EVENTS.ROUTING:
      return <RoutingPanel payload={event.data} />;
    case SSE_EVENTS.EXPERT_RESPONSE:
      return <ExpertResponseCard payload={event.data} />;
    case SSE_EVENTS.FINAL:
      return <ExpertResponseCard payload={event.data} isFinal />;
    case SSE_EVENTS.REASONING:
      return <ReasoningLine text={event.data.text} />;
    case SSE_EVENTS.TOOL_CALL:
      return <ToolEventLine kind="call" tool={event.data.tool} payload={event.data.input} />;
    case SSE_EVENTS.TOOL_RESULT:
      return <ToolEventLine kind="result" tool={event.data.tool} payload={event.data.output} />;
    case SSE_EVENTS.DONE:
      return null;
  }
}
