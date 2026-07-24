import React, { useState } from 'react';
import { FileText, Download, CheckCircle2, AlertTriangle, PlusCircle, MinusCircle, RefreshCw } from 'lucide-react';
import { CompareResponse } from '../types';

interface DeltaReportViewProps {
  sessionData: CompareResponse;
}

export const DeltaReportView: React.FC<DeltaReportViewProps> = ({ sessionData }) => {
  const [viewFormat, setViewFormat] = useState<'table' | 'markdown' | 'json'>('table');
  const [filterType, setFilterType] = useState<string>('all');

  const { delta_result, ai_summary } = sessionData;
  const summary = delta_result.summary;

  const filteredItems = delta_result.items.filter(item => {
    if (item.change_type === 'Unchanged') return false;
    if (filterType === 'all') return true;
    return item.change_type.toLowerCase() === filterType.toLowerCase() || item.object_type.toLowerCase() === filterType.toLowerCase();
  });

  return (
    <div className="space-y-6 max-w-6xl">
      {/* AI Executive Summary Banner */}
      <div className="glass-panel p-6 rounded-xl border border-slate-800 bg-gradient-to-r from-sky-950/40 via-slate-900 to-indigo-950/30">
        <h2 className="text-lg font-bold text-sky-400 mb-3 flex items-center gap-2">
          <FileText className="w-5 h-5" />
          AI Change Executive Summary
        </h2>
        <div className="text-slate-200 text-sm leading-relaxed font-sans whitespace-pre-line">
          {ai_summary}
        </div>
      </div>

      {/* Summary Matrix Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="glass-panel p-4 rounded-xl border border-slate-800 text-center">
          <div className="text-xs text-slate-400 font-medium uppercase tracking-wider mb-1">Total Changes</div>
          <div className="text-2xl font-black text-white">{summary.total_changes}</div>
        </div>
        <div className="glass-panel p-4 rounded-xl border border-slate-800 text-center">
          <div className="text-xs text-emerald-400 font-medium uppercase tracking-wider mb-1">Added</div>
          <div className="text-2xl font-black text-emerald-400">{summary.added}</div>
        </div>
        <div className="glass-panel p-4 rounded-xl border border-slate-800 text-center">
          <div className="text-xs text-red-400 font-medium uppercase tracking-wider mb-1">Removed</div>
          <div className="text-2xl font-black text-red-400">{summary.removed}</div>
        </div>
        <div className="glass-panel p-4 rounded-xl border border-slate-800 text-center">
          <div className="text-xs text-amber-400 font-medium uppercase tracking-wider mb-1">Modified</div>
          <div className="text-2xl font-black text-amber-400">{summary.modified}</div>
        </div>
        <div className="glass-panel p-4 rounded-xl border border-slate-800 text-center">
          <div className="text-xs text-sky-400 font-medium uppercase tracking-wider mb-1">Confidence</div>
          <div className="text-2xl font-black text-sky-400">{Math.round(delta_result.overall_confidence * 100)}%</div>
        </div>
      </div>

      {/* Report Controls & Format Tabs */}
      <div className="glass-panel p-6 rounded-xl border border-slate-800">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div className="flex items-center gap-2 bg-slate-900 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setViewFormat('table')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                viewFormat === 'table' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Interactive Table
            </button>
            <button
              onClick={() => setViewFormat('markdown')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                viewFormat === 'markdown' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Markdown View
            </button>
            <button
              onClick={() => setViewFormat('json')}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                viewFormat === 'json' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Raw JSON
            </button>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-400 font-medium">Filter:</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-slate-900 text-slate-200 border border-slate-800 rounded-lg px-3 py-1.5 text-xs font-medium focus:outline-none focus:border-sky-500"
            >
              <option value="all">All Changes</option>
              <option value="added">Added Only</option>
              <option value="removed">Removed Only</option>
              <option value="modified">Modified Only</option>
              <option value="valve">Valves</option>
              <option value="instrument">Instruments</option>
            </select>
          </div>
        </div>

        {/* View Switch */}
        {viewFormat === 'table' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400">
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Type</th>
                  <th className="py-3 px-4">Tag</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4">Page</th>
                  <th className="py-3 px-4">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-sm">
                {filteredItems.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-900/40">
                    <td className="py-3.5 px-4">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-bold ${
                        item.change_type === 'Added'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : item.change_type === 'Removed'
                          ? 'bg-red-500/10 text-red-400 border border-red-500/30'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      }`}>
                        {item.change_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-medium">{item.object_type}</td>
                    <td className="py-3.5 px-4 font-mono text-sky-400 font-semibold">{item.tag || '-'}</td>
                    <td className="py-3.5 px-4 text-slate-400 text-xs leading-relaxed">{item.description}</td>
                    <td className="py-3.5 px-4 text-slate-400 text-xs font-mono">
                      Page {item.page_a || item.page_b || 1}
                    </td>
                    <td className="py-3.5 px-4 text-emerald-400 font-mono text-xs font-bold">
                      {Math.round(item.confidence * 100)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {viewFormat === 'markdown' && (
          <div className="bg-slate-950 p-4 rounded-lg font-mono text-xs text-slate-300 overflow-x-auto border border-slate-800 max-h-[500px]">
            <pre>{sessionData.delta_result ? JSON.stringify(sessionData.delta_result, null, 2) : ''}</pre>
          </div>
        )}

        {viewFormat === 'json' && (
          <div className="bg-slate-950 p-4 rounded-lg font-mono text-xs text-sky-300 overflow-x-auto border border-slate-800 max-h-[500px]">
            <pre>{JSON.stringify(delta_result, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};
