import React, { useState } from 'react';
import { UploadCloud, FileText, Loader2, Cpu, CheckCircle } from 'lucide-react';
import { compareDocuments } from '../services/api';
import { CompareResponse } from '../types';

interface UploadPanelProps {
  onComparisonComplete: (data: CompareResponse) => void;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({ onComparisonComplete }) => {
  const [fileA, setFileA] = useState<File | null>(null);
  const [fileB, setFileB] = useState<File | null>(null);
  const [adapterType, setAdapterType] = useState<string>('pdf');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunComparison = async () => {
    if (!fileA || !fileB) {
      setError('Please select both Revision A and Revision B documents.');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const data = await compareDocuments(fileA, fileB, adapterType);
      onComparisonComplete(data);
    } catch (err: any) {
      setError(err.message || 'Error processing documents.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="glass-panel p-6 rounded-xl border border-slate-800">
        <h2 className="text-xl font-bold text-white mb-2">Ingest Document Revisions</h2>
        <p className="text-sm text-slate-400 mb-6">
          Upload Revision A (baseline) and Revision B (updated). Select the format adapter below.
        </p>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* File A Dropzone */}
          <div className="border-2 border-dashed border-slate-700 hover:border-sky-500/50 rounded-xl p-6 flex flex-col items-center justify-center bg-slate-900/40 transition-colors">
            <UploadCloud className="w-8 h-8 text-sky-400 mb-3" />
            <h3 className="text-sm font-semibold text-white mb-1">Revision A (Baseline)</h3>
            <p className="text-xs text-slate-500 mb-4 text-center">PDF or DWG engineering diagram</p>
            <input
              type="file"
              id="file-a-input"
              className="hidden"
              onChange={(e) => e.target.files && setFileA(e.target.files[0])}
            />
            <label
              htmlFor="file-a-input"
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 cursor-pointer border border-slate-700"
            >
              {fileA ? fileA.name : 'Select Revision A'}
            </label>
          </div>

          {/* File B Dropzone */}
          <div className="border-2 border-dashed border-slate-700 hover:border-sky-500/50 rounded-xl p-6 flex flex-col items-center justify-center bg-slate-900/40 transition-colors">
            <UploadCloud className="w-8 h-8 text-emerald-400 mb-3" />
            <h3 className="text-sm font-semibold text-white mb-1">Revision B (Updated)</h3>
            <p className="text-xs text-slate-500 mb-4 text-center">PDF or DWG engineering diagram</p>
            <input
              type="file"
              id="file-b-input"
              className="hidden"
              onChange={(e) => e.target.files && setFileB(e.target.files[0])}
            />
            <label
              htmlFor="file-b-input"
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 cursor-pointer border border-slate-700"
            >
              {fileB ? fileB.name : 'Select Revision B'}
            </label>
          </div>
        </div>

        {/* Adapter Selector */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 mb-6">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-3">
            Ingestion Format Adapter
          </label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'pdf', label: 'Native PDF', desc: 'Vector layout parsing' },
              { id: 'ocr', label: 'Scanned PDF', desc: 'PyMuPDF + EasyOCR' },
              { id: 'dwg', label: 'DWG Stub', desc: 'CAD layers & blocks' },
            ].map((adapter) => (
              <button
                key={adapter.id}
                type="button"
                onClick={() => setAdapterType(adapter.id)}
                className={`p-3 rounded-lg border text-left transition-all ${
                  adapterType === adapter.id
                    ? 'border-sky-500 bg-sky-500/10 text-white'
                    : 'border-slate-800 bg-slate-950 text-slate-400 hover:bg-slate-900'
                }`}
              >
                <div className="text-sm font-bold">{adapter.label}</div>
                <div className="text-[11px] text-slate-500 mt-0.5">{adapter.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleRunComparison}
          disabled={loading || !fileA || !fileB}
          className={`w-full py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
            loading || !fileA || !fileB
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white shadow-lg shadow-sky-500/25'
          }`}
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Parsing Canonical Models & Computing Weighted Delta...
            </>
          ) : (
            <>
              <Cpu className="w-5 h-5" />
              Run Delta Engine Comparison
            </>
          )}
        </button>
      </div>
    </div>
  );
};
