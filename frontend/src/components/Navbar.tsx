import React from 'react';
import { 
  LayoutDashboard, 
  UploadCloud, 
  Eye, 
  FileText, 
  MessageSquare, 
  Activity, 
  Award,
  Layers
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  hasSession: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, hasSession }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload & Ingest', icon: UploadCloud },
    { id: 'visual', label: 'Visual Diff', icon: Eye, disabled: !hasSession },
    { id: 'report', label: 'Delta Report', icon: FileText, disabled: !hasSession },
    { id: 'chat', label: 'Grounded Chat', icon: MessageSquare, disabled: !hasSession },
    { id: 'logs', label: 'Logs & Tracing', icon: Activity },
    { id: 'eval', label: 'Evaluation', icon: Award },
  ];

  return (
    <aside className="w-64 glass-panel border-r border-slate-800 flex flex-col justify-between p-4 min-h-screen">
      <div>
        <div className="flex items-center gap-3 px-3 py-4 mb-6 border-b border-slate-800">
          <div className="p-2 bg-gradient-to-tr from-sky-500 to-indigo-600 rounded-lg shadow-lg shadow-sky-500/20">
            <Layers className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-white tracking-tight">DeltaDoc AI</h1>
            <p className="text-xs text-sky-400 font-medium">Revision Intelligence</p>
          </div>
        </div>

        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                disabled={item.disabled}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium text-sm transition-all duration-200 ${
                  isActive
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30 shadow-sm'
                    : item.disabled
                    ? 'text-slate-600 cursor-not-allowed opacity-50'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800/80">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-slate-400 font-medium">System Status</span>
          <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Ready
          </span>
        </div>
        <p className="text-[11px] text-slate-500">Gemini 2.5 Flash • ChromaDB</p>
      </div>
    </aside>
  );
};
