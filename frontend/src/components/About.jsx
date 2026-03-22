import { Link } from "react-router-dom";

const pipeline = [
  { step: "1", title: "Upload or paste a URL", desc: "Drop in a PDF or point DocSignal at any documentation site. It crawls up to 25 pages automatically." },
  { step: "2", title: "Text is extracted and chunked", desc: "The content is split into overlapping 512-token passages — small enough to be precise, large enough to preserve context." },
  { step: "3", title: "Each chunk is embedded", desc: "A local embedding model converts every passage into a 384-dimensional vector — a numerical fingerprint of its meaning." },
  { step: "4", title: "Vectors are stored in pgvector", desc: "The embeddings are stored in PostgreSQL with the pgvector extension, enabling fast cosine similarity search at scale." },
  { step: "5", title: "You ask a question", desc: "Your question is embedded the same way, then compared against every stored chunk using cosine similarity." },
  { step: "6", title: "Answer + cited sources", desc: "The top matching passages are fed to an LLM, which synthesizes a direct answer and shows you exactly where it came from." },
];

const achievements = [
  "End-to-end vector search pipeline: ingest → chunk → embed → store → retrieve",
  "pgvector cosine similarity search over 500–800 chunk embeddings per doc set",
  "Three pre-loaded documentation sets (FastAPI, SQLite, Requests) with zero setup",
  "PDF upload and URL crawl ingestion with configurable depth limit",
  "Groq LLM Q&A synthesis (llama-3.1-8b-instant) with cited source passages and similarity scores",
  "Analytics dashboard: query frequency, source heatmap, volume over time",
  "Embedding provider switchable between fastembed (local, free) and OpenAI",
  "Deployed to Hugging Face Spaces with Neon serverless PostgreSQL",
];

const stack = [
  { name: "FastAPI", role: "REST API backend" },
  { name: "pgvector", role: "Vector similarity search" },
  { name: "PostgreSQL / Neon", role: "Relational + vector database" },
  { name: "fastembed", role: "Local embedding model (BAAI/bge-small-en-v1.5)" },
  { name: "Groq", role: "LLM answer synthesis (llama-3.1-8b-instant)" },
  { name: "React + Vite", role: "Frontend UI" },
  { name: "Tailwind CSS", role: "Styling" },
  { name: "Recharts", role: "Analytics charts" },
  { name: "Docker", role: "Local development environment" },
  { name: "Hugging Face Spaces", role: "Production hosting" },
];

export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12 flex flex-col gap-12">
      {/* Hero */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-4">DocSignal</h1>
        <p className="text-gray-300 text-base leading-relaxed">
          A keyword search finds the word. This finds the meaning.
        </p>
        <p className="text-gray-400 text-sm leading-relaxed mt-3">
          DocSignal ingests documentation — PDFs or live websites — and answers natural language questions
          against the content, showing exactly which passage the answer came from. It doesn't match
          keywords; it understands what you're asking and finds the most semantically relevant answer
          across the entire document set.
        </p>
      </div>

      {/* How It Works */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-6">How It Works</h2>
        <div className="flex flex-col">
          {pipeline.map((item, i) => (
            <div key={i} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className="w-8 h-8 rounded-full bg-cyan-600 flex items-center justify-center text-white text-sm font-bold shrink-0">
                  {item.step}
                </div>
                {i < pipeline.length - 1 && <div className="w-px flex-1 bg-gray-700 my-1" />}
              </div>
              <div className="pb-8">
                <p className="text-sm font-medium text-white mb-1">{item.title}</p>
                <p className="text-sm text-gray-400">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* What Was Built */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">What Was Built</h2>
        <ul className="flex flex-col gap-2">
          {achievements.map((a, i) => (
            <li key={i} className="flex gap-2 text-sm text-gray-400">
              <span className="text-cyan-500 shrink-0">✓</span>
              {a}
            </li>
          ))}
        </ul>
      </div>

      {/* Tech Stack */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Tech Stack</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {stack.map((s) => (
            <div key={s.name} className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-3">
              <p className="text-sm font-medium text-white">{s.name}</p>
              <p className="text-xs text-gray-500 mt-0.5">{s.role}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Links */}
      <div className="flex gap-4">
        <Link
          to="/"
          className="px-6 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium rounded-lg transition-colors"
        >
          Try the App
        </Link>
        <a
          href="https://github.com/eholt723/docsignal"
          target="_blank"
          rel="noopener noreferrer"
          className="px-6 py-2.5 bg-gray-800 border border-gray-700 hover:border-cyan-600 text-gray-300 hover:text-white text-sm font-medium rounded-lg transition-colors"
        >
          View on GitHub
        </a>
      </div>
    </div>
  );
}
