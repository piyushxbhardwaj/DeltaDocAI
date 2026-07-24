import React, { useEffect, useState } from 'react';
import { Activity, Clock, Terminal, Zap } from 'lucide-react';
import { fetchMetrics } from '../services/api';

export const LogsViewer: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    fetchMetrics().then(setMetrics).catch(console.error);
  }, []);

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="glass-panel p-6 rounded-xl border border-slate-800">
        <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
          <Activity className="w-5 h-5 text-sky-400" />
          Observability & Unified JSON Telemetry Traces
        </h2>
        <p className="text-sm text-slate-400 mb-6">
          Every request generates a unique Trace ID, recording step latencies (OCR, embedding, vector retrieval, LLM), token counts, and cost metrics.
        </p>

        {metrics ? (
          <div className="space-y-4">
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-sky-400 overflow-x-auto max-h-[500px]">
              <pre>{JSON.stringify(metrics, null, 2)}</pre>
            </div>
          </div>
        ) : (
          <div className="text-slate-500 text-sm">Loading telemetry logs...</div>
        )}
      </div>
    </div>
  );
};
