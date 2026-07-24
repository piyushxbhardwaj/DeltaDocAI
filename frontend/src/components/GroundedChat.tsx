import React, { useState } from 'react';
import { MessageSquare, Send, ShieldCheck, Sparkles, BookOpen, Loader2 } from 'lucide-react';
import { sendChatQuery } from '../services/api';
import { ChatResponse, CompareResponse } from '../types';

interface GroundedChatProps {
  sessionData: CompareResponse;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  citations?: any[];
  groundedness?: number;
  tokens?: number;
  cost?: number;
}

export const GroundedChat: React.FC<GroundedChatProps> = ({ sessionData }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'ai',
      text: `Hello! I am **DeltaDoc AI**. I have indexed Revision A, Revision B, and the generated Delta Report for session **${sessionData.session_id}**. Ask me any question about modifications, removed valves, or equipment locations.`,
    },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userText = query.trim();
    setQuery('');

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: userText,
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res: ChatResponse = await sendChatQuery(sessionData.session_id, userText);
      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: res.answer,
        citations: res.citations,
        groundedness: res.groundedness_score,
        tokens: res.prompt_tokens + res.completion_tokens,
        cost: res.estimated_cost_usd,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          text: `Error processing query: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = [
    'What changed between Revision A and B?',
    'Which valves were removed?',
    'Which compressor was modified?',
    'Where is 26-PIT-9055?',
  ];

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="glass-panel p-6 rounded-xl border border-slate-800 flex flex-col h-[650px]">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-sky-400" />
            <h2 className="font-bold text-white text-lg">Grounded RAG Chat</h2>
          </div>
          <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 font-semibold">
            <ShieldCheck className="w-4 h-4" />
            Strict Retrieval Grounding
          </div>
        </div>

        {/* Suggested Quick Questions */}
        <div className="flex flex-wrap gap-2 mb-4">
          {sampleQuestions.map((sq, i) => (
            <button
              key={i}
              onClick={() => setQuery(sq)}
              className="text-xs bg-slate-900 hover:bg-slate-800 text-sky-300 px-3 py-1.5 rounded-lg border border-slate-800 transition-colors"
            >
              {sq}
            </button>
          ))}
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-2">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed ${
                  m.sender === 'user'
                    ? 'bg-sky-600 text-white rounded-br-none'
                    : 'bg-slate-900 text-slate-200 border border-slate-800 rounded-bl-none'
                }`}
              >
                <div className="whitespace-pre-line">{m.text}</div>

                {/* Citations Card */}
                {m.citations && m.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-1.5">
                    <div className="text-[11px] font-bold text-sky-400 uppercase tracking-wider flex items-center gap-1">
                      <BookOpen className="w-3 h-3" />
                      Retrieved Citations
                    </div>
                    {m.citations.map((c, idx) => (
                      <div key={idx} className="bg-slate-950/70 p-2 rounded border border-slate-800 text-xs font-mono">
                        <span className="text-emerald-400 font-bold">[{c.source}{c.page ? `, Page ${c.page}` : ''}]</span>
                        <span className="text-slate-400 ml-2">{c.snippet}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {m.cost !== undefined && (
                <div className="text-[10px] text-slate-500 mt-1 px-1">
                  Tokens: {m.tokens} • Cost: ${m.cost.toFixed(5)} • Groundedness: {Math.round((m.groundedness || 1) * 100)}%
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-slate-400 text-xs py-2">
              <Loader2 className="w-4 h-4 animate-spin text-sky-400" />
              Searching ChromaDB vector store & generating grounded response...
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="mt-4 flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask about document differences, valves, instruments..."
            className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-5 py-3 rounded-xl bg-sky-500 hover:bg-sky-400 disabled:bg-slate-800 text-white font-semibold text-sm transition-all flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
