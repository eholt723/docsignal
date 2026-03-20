import { useState } from "react";

export default function UploadPanel({ onIngested }) {
  const [url, setUrl] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

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
        <p className="text-xs text-gray-500 uppercase tracking-wide">Ingest from URL (max 25 pages)</p>
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
        <div className="bg-gray-800 border border-gray-700 rounded-xl px-5 py-3 text-sm text-gray-300">
          <span className="text-cyan-500 font-medium">{result.doc_name}</span> ingested —{" "}
          {result.chunks_stored} chunks stored.
        </div>
      )}
    </div>
  );
}
