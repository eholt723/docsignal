import { useState } from "react";

export default function AskPanel({ activePreset, prefillQuestion, onQuestionClear }) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [citationsOpen, setCitationsOpen] = useState(false);

  // Sync prefilled question from example chips
  if (prefillQuestion && prefillQuestion !== question) {
    setQuestion(prefillQuestion);
    onQuestionClear?.();
  }

  async function handleAsk() {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setCitationsOpen(false);

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, doc_set: activePreset || null }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="Ask a question about the docs..."
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-600"
        />
        <button
          onClick={handleAsk}
          disabled={loading || !question.trim()}
          className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && (
        <div className="flex flex-col gap-3">
          <div className="bg-gray-800 border border-gray-700 rounded-xl px-5 py-4">
            <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Answer</p>
            <p className="text-sm text-gray-100 whitespace-pre-wrap leading-relaxed">{result.answer}</p>
          </div>

          {result.citations?.length > 0 && (
            <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
              <button
                onClick={() => setCitationsOpen((o) => !o)}
                className="w-full flex justify-between items-center px-5 py-3 text-sm text-gray-400 hover:text-white transition-colors"
              >
                <span>Sources ({result.citations.length})</span>
                <span>{citationsOpen ? "▲" : "▼"}</span>
              </button>

              {citationsOpen && (
                <div className="border-t border-gray-700 divide-y divide-gray-700">
                  {result.citations.map((c, i) => (
                    <div key={i} className="px-5 py-3">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-xs font-medium text-cyan-500">{c.doc_name}</span>
                        <span className="text-xs text-gray-500">
                          similarity: {(c.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 leading-relaxed line-clamp-4">{c.text}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
