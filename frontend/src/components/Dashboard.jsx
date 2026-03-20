import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid,
} from "recharts";

function StatCard({ label, value }) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl px-5 py-4">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-semibold text-white">{value ?? "—"}</p>
    </div>
  );
}

export default function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [topQuestions, setTopQuestions] = useState([]);
  const [topSources, setTopSources] = useState([]);
  const [volume, setVolume] = useState([]);
  const [simDist, setSimDist] = useState([]);

  useEffect(() => {
    fetch("/api/analytics/overview").then((r) => r.json()).then(setOverview).catch(() => {});
    fetch("/api/analytics/top-questions?limit=5").then((r) => r.json()).then(setTopQuestions).catch(() => {});
    fetch("/api/analytics/top-sources?limit=5").then((r) => r.json()).then(setTopSources).catch(() => {});
    fetch("/api/analytics/query-volume?days=30").then((r) => r.json()).then(setVolume).catch(() => {});
    fetch("/api/analytics/similarity-distribution").then((r) => r.json()).then(setSimDist).catch(() => {});
  }, []);

  return (
    <div className="flex flex-col gap-8">
      {/* Overview stats */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Total Queries" value={overview?.total_queries} />
        <StatCard label="Documents" value={overview?.total_documents} />
        <StatCard label="Chunks Stored" value={overview?.total_chunks} />
      </div>

      {/* Query volume over time */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl px-5 py-4">
        <p className="text-sm font-semibold text-white mb-4">Query Volume (Last 30 Days)</p>
        {volume.length ? (
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={volume}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} tickLine={false} />
              <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: 8 }} />
              <Line type="monotone" dataKey="count" stroke="#06b6d4" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-gray-500">No queries yet.</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Top questions */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl px-5 py-4">
          <p className="text-sm font-semibold text-white mb-3">Most Asked Questions</p>
          {topQuestions.length ? (
            <div className="flex flex-col gap-2">
              {topQuestions.map((q, i) => (
                <div key={i} className="flex justify-between gap-2 text-xs text-gray-400">
                  <span className="truncate">{q.query_text}</span>
                  <span className="text-cyan-500 shrink-0">{q.count}x</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No queries yet.</p>
          )}
        </div>

        {/* Top sources */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl px-5 py-4">
          <p className="text-sm font-semibold text-white mb-3">Most Referenced Sources</p>
          {topSources.length ? (
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={topSources} layout="vertical">
                <XAxis type="number" tick={{ fill: "#6b7280", fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis type="category" dataKey="doc_name" tick={{ fill: "#9ca3af", fontSize: 11 }} tickLine={false} width={100} />
                <Tooltip contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: 8 }} />
                <Bar dataKey="citation_count" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-sm text-gray-500">No data yet.</p>
          )}
        </div>
      </div>

      {/* Similarity distribution */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl px-5 py-4">
        <p className="text-sm font-semibold text-white mb-4">Similarity Score Distribution</p>
        {simDist.length ? (
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={simDist}>
              <XAxis dataKey="bucket" tick={{ fill: "#6b7280", fontSize: 11 }} tickLine={false} />
              <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: "#1f2937", border: "1px solid #374151", borderRadius: 8 }} />
              <Bar dataKey="count" fill="#06b6d4" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-gray-500">No queries yet.</p>
        )}
      </div>
    </div>
  );
}
