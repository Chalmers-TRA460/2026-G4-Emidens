import { useNavigate } from "react-router-dom";
import { WelcomeView } from "../components/live/WelcomeView";
import { useActiveRun } from "../ActiveRunContext";

export function NewRunPage() {
  const navigate = useNavigate();
  const { submit } = useActiveRun();

  const handleSubmit = (query: string) => {
    const id = submit(query);
    navigate(`/sessions/${id}`);
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 min-h-0">
      <WelcomeView onSubmit={handleSubmit} />
    </div>
  );
}
