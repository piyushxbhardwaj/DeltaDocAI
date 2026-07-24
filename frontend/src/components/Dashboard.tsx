import React from 'react';
import { UploadCloud, FileDiff, ShieldCheck, Zap, ArrowRight } from 'lucide-react';

interface DashboardProps {
  onStartUpload: () => void;
  hasSession: boolean;
  onViewReport: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onStartUpload, hasSession, onViewReport }) => {
  return (
    <div className="space-y-8 max-w-6xl">
      <div className="glass-panel p-8 rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900 to-sky-950/40 relative overflow-hidden">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-semibold mb-4">
            <Zap className="w-3.5 h-3.5" />
            Applied AI Engineering Architecture
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl mb-4">
            AI-Powered Engineering Document Comparison & Grounded Chat
          </h2>
          <p className="text-slate-400 text-base leading-relaxed mb-6">
            DeltaDoc AI ingests P&ID diagrams, engineering PDFs, and DWG drawings into a unified canonical model, computes high-precision weighted deltas, generates annotated visual diffs, and indexes structured context for hallucination-free RAG chat.
          </p>
          <div className="flex gap-4">
            <button
              onClick={onStartUpload}
              className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-sky-500/25 transition-all duration-200"
            >
              <UploadCloud className="w-4 h-4" />
              Upload Document Revisions
            </button>
            {hasSession && (
              <button
                onClick={onViewReport}
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm border border-slate-700 transition-all duration-200"
              >
                <FileDiff className="w-4 h-4 text-sky-400" />
                View Current Delta Report
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-xl border border-slate-800">
          <div className="p-3 bg-emerald-500/10 w-fit rounded-lg text-emerald-400 mb-4 border border-emerald-500/20">
            <FileDiff className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">Weighted Scoring Delta</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Combines 40% Tag matching, 25% Spatial IoU bounding box overlap, 20% String distance, and 15% Element type similarity.
          </p>
        </div>

        <div className="glass-panel p-6 rounded-xl border border-slate-800">
          <div className="p-3 bg-sky-500/10 w-fit rounded-lg text-sky-400 mb-4 border border-sky-500/20">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">Grounded RAG Chat</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Indexes structured hierarchical page chunks in ChromaDB. Provides exact citations for every answer with zero hallucination.
          </p>
        </div>

        <div className="glass-panel p-6 rounded-xl border border-slate-800">
          <div className="p-3 bg-indigo-500/10 w-fit rounded-lg text-indigo-400 mb-4 border border-indigo-500/20">
            <Zap className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">End-to-End Tracing</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Measures OCR, embedding, retrieval, and LLM latencies per request, recording structured JSON logs and cost metrics.
          </p>
        </div>
      </div>
    </div>
  );
};
