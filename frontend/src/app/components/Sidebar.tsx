import { MessageSquarePlus, Clock, Bot, Database, Settings } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const navItems = [
  { icon: MessageSquarePlus, label: 'New Chat', to: '/new' },
  { icon: Clock, label: 'Sessions', to: '/' },
  { icon: Bot, label: 'Agents', to: '/agents' },
  { icon: Database, label: 'Knowledge', to: '/knowledge' },
  { icon: Settings, label: 'Settings', to: '/settings' },
];

export function Sidebar() {
  return (
    <div className="w-60 bg-[#0f1a2e] text-white flex flex-col h-full">
      <div className="px-5 pt-5 pb-4 mb-2 border-b border-white/20">
        <div className="font-bold text-xl">Konsult</div>
      </div>

      <nav className="flex-1 px-3">
        {navItems.map((item) => (
          <NavLink
            key={item.label}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `w-full flex items-center gap-3 px-3 py-2.5 rounded-md mb-0.5 transition-colors text-sm ${
                isActive
                  ? 'bg-[#1e2d4a] text-white'
                  : 'text-blue-200 hover:bg-[#162240] hover:text-white'
              }`
            }
          >
            <item.icon className="w-4 h-4" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
