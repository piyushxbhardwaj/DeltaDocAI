import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Dashboard } from './components/Dashboard';
import { UploadPanel } from './components/UploadPanel';
import { VisualDiffViewer } from './components/VisualDiffViewer';
import { DeltaReportView } from './components/DeltaReportView';
import { GroundedChat } from './components/GroundedChat';
import { LogsViewer } from './components/LogsViewer';
import { EvalScorecard } from './components/EvalScorecard';
import { CompareResponse } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [sessionData, setSessionData] = useState<CompareResponse | null>(null);

  const handleComparisonComplete = (data: CompareResponse) => {
    setSessionData(data);
    setActiveTab('visual');
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        hasSession={!!sessionData}
      />

      <main className="flex-1 p-8 overflow-y-auto">
        {activeTab === 'dashboard' && (
          <Dashboard
            onStartUpload={() => setActiveTab('upload')}
            hasSession={!!sessionData}
            onViewReport={() => setActiveTab('report')}
          />
        )}

        {activeTab === 'upload' && (
          <UploadPanel onComparisonComplete={handleComparisonComplete} />
        )}

        {activeTab === 'visual' && sessionData && (
          <VisualDiffViewer sessionData={sessionData} />
        )}

        {activeTab === 'report' && sessionData && (
          <DeltaReportView sessionData={sessionData} />
        )}

        {activeTab === 'chat' && sessionData && (
          <GroundedChat sessionData={sessionData} />
        )}

        {activeTab === 'logs' && <LogsViewer />}

        {activeTab === 'eval' && (
          <EvalScorecard sessionId={sessionData?.session_id} />
        )}
      </main>
    </div>
  );
};
