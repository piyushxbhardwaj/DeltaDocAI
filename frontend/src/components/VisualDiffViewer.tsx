import React from 'react';
import { Eye, Layers, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { CompareResponse } from '../types';

interface VisualDiffViewerProps {
  sessionData: CompareResponse;
}

export const VisualDiffViewer: React.FC<VisualDiffViewerProps> = ({ sessionData }) => {
  const visualDiffUrl = `/api/visual-diff?session_id=${sessionData.session_id}`;

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="glass-panel p-6 rounded-xl border border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
            <Eye className="w-5 h-5 text-sky-400" />
            Visual Bounding Box Overlay Diff
          </h2>
          <p className="text-sm text-slate-400">
            Session ID: <span className="font-mono text-sky-400">{sessionData.session_id}</span>
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 bg-slate-900/80 px-4 py-2 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
            <span className="w-3 h-3 rounded bg-emerald-500/30 border border-emerald-500"></span>
            Added
          </div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-red-400">
            <span className="w-3 h-3 rounded bg-red-500/30 border border-red-500"></span>
            Removed
          </div>
          <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-400">
            <span className="w-3 h-3 rounded bg-amber-500/30 border border-amber-500"></span>
            Modified
          </div>
        </div>
      </div>

      <div className="glass-panel p-4 rounded-xl border border-slate-800 bg-slate-950 min-h-[500px] flex items-center justify-center overflow-auto">
        <img
          src={visualDiffUrl}
          alt="Visual Diff Overlay"
          className="max-w-full rounded-lg shadow-2xl border border-slate-800"
          onError={(e) => {
            (e.target as HTMLElement).style.display = 'none';
          }}
        />
      </div>
    </div>
  );
};
