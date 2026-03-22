export default function PresetBar({ activePreset, onSelect }) {
  const presets = [
    { key: "fastapi", label: "FastAPI" },
    { key: "sqlite", label: "SQLite" },
    { key: "requests", label: "Requests" },
  ];

  return (
    <div className="flex gap-2 flex-wrap">
      {presets.map((p) => (
        <button
          key={p.key}
          onClick={() => onSelect(p.key)}
          className={`px-4 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
            activePreset === p.key
              ? "bg-cyan-600 border-cyan-600 text-white"
              : "bg-gray-800 border-gray-700 text-gray-300 hover:border-cyan-600 hover:text-white"
          }`}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
}
