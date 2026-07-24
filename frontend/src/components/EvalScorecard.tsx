import React, { useEffect, useState } from 'react';
import { Award, CheckCircle, BarChart2, ShieldCheck, DollarSign, Clock } from 'lucide-react';
import { fetchEvaluation } from '../services/api';
import { Scorecard } from '../types';

interface EvalScorecardProps {
  sessionId?: string;
}

export const EvalScorecard: React.FC<EvalScorecardProps> = ({ sessionId }) => {
  const [scorecard, setScorecard] = useState<Scorecard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvaluation(sessionId)
      .then(setScorecard)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) {
    return <div className="text-slate-400 text-sm">Calculating quantitative AI evaluation metrics...</div>;
  }

  if (!scorecard) {
    return <div className="text-red-400 text-sm">Failed to load evaluation scorecard.</div>;
  }

  const metricsList = [
    { label: 'Delta Detection Precision', value: `${Math.round(scorecard.delta_precision * 100)}%`, color: 'text-emerald-400' },
    { label: 'Delta Detection Recall', value: `${Math.round(scorecard.delta_recall * 100)}%`, color: 'text-emerald-400' },
    { label: 'Delta Detection F1 Score', value: `${scorecard.delta_f1}`, color: 'text-sky-400' },
    { label: 'RAG Groundedness Score', value: `${Math.round(scorecard.groundedness_score * 100)}%`, color: 'text-emerald-400' },
    { label: 'Hallucination Rate', value: `${Math.round(scorecard.hallucination_rate * 100)}%`, color: 'text-emerald-400' },
    { label: 'Citation Accuracy', value: `${Math.round(scorecard.citation_accuracy * 100)}%`, color: 'text-sky-400' },
    { label: 'Retrieval Recall@k', value: `${Math.round(scorecard.retrieval_recall_at_k * 100)}%`, color: 'text-indigo-400' },
    { label: 'OCR Extraction Accuracy', value: `${Math.round(scorecard.ocr_accuracy * 100)}%`, color: 'text-emerald-400' },
  ];

  return (
    <div className="space-y-6 max-w-5xl">
      <div className="glass-panel p-6 rounded-xl border border-slate-800">
        <div className="flex items-center gap-3 mb-2">
          <Award className="w-6 h-6 text-amber-400" />
          <h2 className="text-xl font-bold text-white">DeltaDoc AI Evaluation Scorecard</h2>
        </div>
        <p className="text-sm text-slate-400 mb-6">
          Quantitative benchmarking metrics calculated across document delta precision/recall, RAG groundedness, hallucination rate, and citation accuracy.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {metricsList.map((m, idx) => (
            <div key={idx} className="glass-panel p-4 rounded-xl border border-slate-800/80 bg-slate-950/60">
              <div className="text-xs font-semibold text-slate-400 mb-1">{m.label}</div>
              <div className={`text-2xl font-black ${m.color}`}>{m.value}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Clock className="w-5 h-5 text-sky-400" />
              <div>
                <div className="text-xs text-slate-400 font-medium">Avg Response Latency</div>
                <div className="text-lg font-bold text-white">{scorecard.avg_response_latency_ms} ms</div>
              </div>
            </div>
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <DollarSign className="w-5 h-5 text-emerald-400" />
              <div>
                <div className="text-xs text-slate-400 font-medium">Estimated Pipeline Cost</div>
                <div className="text-lg font-bold text-emerald-400">${scorecard.total_cost_usd} USD</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
