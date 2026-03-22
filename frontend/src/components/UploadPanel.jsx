import { useState } from "react";

export default function UploadPanel({ onIngested }) {
  const [url, setUrl] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [question, setQuestion] = useState("");
  const [askLoading, setAskLoading] = useState(false);
  const [askResult, setAskResult] = useState(null);
  const [askError, setAskError] = useState(null);
  const [citationsOpen, setCitationsOpen] = useState(false);

  async function handleAsk() {
    if (!question.trim()) return;
    setAskLoading(true);
    setAskError(null);
    setAskResult(null);
    setCitationsOpen(false);
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, doc_set: null }),
      });
      if (!res.ok) throw new Error(await res.text());
      setAskResult(await res.json());
    } catch (e) {
      setAskError(e.message);
    } finally {
      setAskLoading(false);
    }
  }

  async function handleUrlIngest() {
    if (!url.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/ingest/url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResult(data);
      onIngested?.(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  async function handlePdfIngest() {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("/api/ingest/pdf", { method: "POST", body: form });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResult(data);
      onIngested?.(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {/* URL ingestion */}
      <div className="flex flex-col gap-2">
        <p className="text-xs text-gray-500 uppercase tracking-wide">Ingest from URL</p>
        <p className="text-xs text-gray-600">
          Crawls up to 25 pages from the starting URL. Works best with static documentation sites.
        </p>
        <p className="text-xs text-gray-600">
          <span className="text-gray-500">Example:</span> https://docs.python-requests.org/en/latest/user/quickstart/
        </p>
        <div className="flex gap-2">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://docs.example.com/"
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-600"
          />
          <button
            onClick={handleUrlIngest}
            disabled={loading || !url.trim()}
            className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
          >
            {loading ? "Ingesting..." : "Ingest"}
          </button>
        </div>
      </div>

      <div className="flex items-center gap-3 text-gray-600">
        <hr className="flex-1 border-gray-700" />
        <span className="text-xs">or</span>
        <hr className="flex-1 border-gray-700" />
      </div>

      {/* PDF ingestion */}
      <div className="flex flex-col gap-2">
        <p className="text-xs text-gray-500 uppercase tracking-wide">Upload PDF</p>
        <p className="text-xs text-gray-600">
          Upload any technical PDF — API references, whitepapers, internal docs, or your own notes.
        </p>
        <p className="text-xs text-gray-600">
          <span className="text-gray-500">Example:</span> download a library's PDF from ReadTheDocs (look for the
          {" "}<span className="text-gray-400">v: latest</span>{" "}menu at the bottom left of any ReadTheDocs site).
        </p>
        <div className="flex gap-2">
          <label className="flex-1 cursor-pointer bg-gray-800 border border-dashed border-gray-700 rounded-lg px-4 py-2 text-sm text-gray-400 hover:border-cyan-600 transition-colors">
            {file ? file.name : "Click to choose a PDF file"}
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => setFile(e.target.files[0])}
            />
          </label>
          <button
            onClick={handlePdfIngest}
            disabled={loading || !file}
            className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
          >
            {loading ? "Ingesting..." : "Upload"}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && (
        <div className="flex flex-col gap-3">
          <div className="bg-gray-800 border border-gray-700 rounded-xl px-5 py-3 text-sm text-gray-300">
            <span className="text-cyan-500 font-medium">{result.doc_name}</span> ingested —{" "}
            {result.chunks_stored} chunks stored.
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAsk()}
              placeholder="Ask a question about your document..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-600"
            />
            <button
              onClick={handleAsk}
              disabled={askLoading || !question.trim()}
              className="px-5 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors"
            >
              {askLoading ? "Thinking..." : "Ask"}
            </button>
          </div>

          {askError && (
            <div className="bg-red-900/30 border border-red-700 rounded-lg px-4 py-3 text-sm text-red-300">
              {askError}
            </div>
          )}

          {askResult && (
            <div className="flex flex-col gap-3">
              <div className="bg-gray-800 border border-gray-700 rounded-xl px-5 py-4">
                <p className="text-xs text-gray-500 uppercase tracking-wide mb-2">Answer</p>
                <p className="text-sm text-gray-100 whitespace-pre-wrap leading-relaxed break-words">{askResult.answer}</p>
              </div>
              {askResult.citations?.length > 0 && (
                <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
                  <button
                    onClick={() => setCitationsOpen((o) => !o)}
                    className="w-full flex justify-between items-center px-5 py-3 text-sm text-gray-400 hover:text-white transition-colors"
                  >
                    <span>Sources ({askResult.citations.length})</span>
                    <span>{citationsOpen ? "▲" : "▼"}</span>
                  </button>
                  {citationsOpen && (
                    <div className="border-t border-gray-700 divide-y divide-gray-700">
                      {askResult.citations.map((c, i) => (
                        <div key={i} className="px-5 py-3">
                          <div className="flex justify-between items-center mb-1">
                            {c.source_url ? (
                              <a href={c.source_url} target="_blank" rel="noopener noreferrer" className="text-xs font-medium text-cyan-500 hover:text-cyan-400 underline underline-offset-2">
                                {c.doc_name}
                              </a>
                            ) : (
                              <span className="text-xs font-medium text-cyan-500">{c.doc_name}</span>
                            )}
                            <span className="text-xs text-gray-500">similarity: {(c.similarity * 100).toFixed(1)}%</span>
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
      )}
    </div>
  );
}
