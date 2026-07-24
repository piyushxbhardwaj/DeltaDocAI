import { CompareResponse, ChatResponse, Scorecard } from '../types';

const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function compareDocuments(
  fileA: File,
  fileB: File,
  adapterType: string = 'pdf'
): Promise<CompareResponse> {
  const formData = new FormData();
  formData.append('file_a', fileA);
  formData.append('file_b', fileB);
  formData.append('adapter_type', adapterType);

  const res = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Comparison failed');
  }

  return res.json();
}

export async function fetchDeltaReport(sessionId: string, format: string = 'json') {
  const res = await fetch(`${API_BASE}/delta?session_id=${sessionId}&format=${format}`);
  if (format === 'html') {
    return res.text();
  }
  if (format === 'markdown') {
    return res.text();
  }
  return res.json();
}

export async function sendChatQuery(sessionId: string, query: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, query, top_k: 5 }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Chat query failed');
  }

  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${API_BASE}/metrics`);
  return res.json();
}

export async function fetchEvaluation(sessionId?: string): Promise<Scorecard> {
  const url = sessionId ? `${API_BASE}/eval?session_id=${sessionId}` : `${API_BASE}/eval`;
  const res = await fetch(url);
  return res.json();
}
