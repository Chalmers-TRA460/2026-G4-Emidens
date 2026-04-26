import { Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { SessionsPage } from './pages/SessionsPage';
import { SessionDetailPage } from './pages/SessionDetailPage';
import { NewRunPage } from './pages/NewRunPage';
import { PlaceholderPage } from './pages/PlaceholderPage';

export default function App() {
  return (
    <div className="size-full flex bg-[#f7f8fa]">
      <Sidebar />

      <Routes>
        <Route path="/" element={<SessionsPage />} />
        <Route path="/sessions/:id" element={<SessionDetailPage />} />
        <Route path="/new" element={<NewRunPage />} />
        <Route path="/agents" element={<PlaceholderPage title="Agents" />} />
        <Route path="/knowledge" element={<PlaceholderPage title="Knowledge" />} />
        <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
      </Routes>
    </div>
  );
}
