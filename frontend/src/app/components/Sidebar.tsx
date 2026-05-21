import { MessageSquarePlus, Clock, Bot, Database, Settings, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const navItems = [
  { icon: MessageSquarePlus, label: 'New Chat', to: '/new' },
  { icon: Clock, label: 'Sessions', to: '/' },
  { icon: Bot, label: 'Agents', to: '/agents' },
  { icon: Database, label: 'Knowledge', to: '/knowledge' },
  { icon: Settings, label: 'Settings', to: '/settings' },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle:  () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  if (collapsed) {
    return (
      <div className="w-12 bg-[#0f1a2e] text-white flex flex-col h-full items-center py-4 gap-2">
        <button
          onClick={onToggle}
          aria-label="Expand sidebar"
          className="p-2 rounded-md text-blue-200 hover:bg-[#162240] hover:text-white"
        >
          <PanelLeftOpen className="w-4 h-4" />
        </button>
        <nav className="flex flex-col gap-1 mt-2">
          {navItems.map((item) => (
            <NavLink
              key={item.label}
              to={item.to}
              end={item.to === '/'}
              title={item.label}
              className={({ isActive }) =>
                `p-2 rounded-md transition-colors ${
                  isActive
                    ? 'bg-[#1e2d4a] text-white'
                    : 'text-blue-200 hover:bg-[#162240] hover:text-white'
                }`
              }
            >
              <item.icon className="w-4 h-4" />
            </NavLink>
          ))}
        </nav>
      </div>
    );
  }

  return (
    <div className="w-60 bg-[#0f1a2e] text-white flex flex-col h-full">
      <div className="px-5 pt-5 pb-4 mb-2 border-b border-white/20">
        <div className="flex items-center gap-3">
          <img src="/logo.svg" alt="" className="w-7 h-7" />
          <div className="font-bold text-xl flex-1">Konsult</div>
          <button
            onClick={onToggle}
            aria-label="Collapse sidebar"
            className="p-1.5 rounded-md text-blue-200 hover:bg-[#162240] hover:text-white"
          >
            <PanelLeftClose className="w-4 h-4" />
          </button>
        </div>
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
