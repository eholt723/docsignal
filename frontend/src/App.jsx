import { useState } from "react";
import { Routes, Route, Link, useLocation } from "react-router-dom";
import PresetBar from "./components/PresetBar.jsx";
import ExampleQuestions from "./components/ExampleQuestions.jsx";
import AskPanel from "./components/AskPanel.jsx";
import UploadPanel from "./components/UploadPanel.jsx";
import Dashboard from "./components/Dashboard.jsx";
import About from "./components/About.jsx";

function Header() {
  const location = useLocation();
  const navLink = (to, label) => (
    <Link
      to={to}
      className={`text-sm transition-colors ${
        location.pathname === to ? "text-white font-medium" : "text-gray-400 hover:text-white"
      }`}
    >
      {label}
    </Link>
  );

  return (
    <header className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
      <Link to="/" className="text-white font-semibold text-base tracking-tight">
        DocSignal
      </Link>
      <nav className="flex gap-6">
        {navLink("/", "Search")}
        {navLink("/upload", "Upload")}
        {navLink("/dashboard", "Dashboard")}
        {navLink("/about", "About")}
      </nav>
    </header>
  );
}

function MainPage() {
  const [activePreset, setActivePreset] = useState("fastapi");
  const [prefillQuestion, setPrefillQuestion] = useState(null);

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Ask the docs</h1>
        <p className="text-sm text-gray-400">
          Select a preset doc set or upload your own, then ask anything.
        </p>
      </div>

      <PresetBar activePreset={activePreset} onSelect={setActivePreset} />

      <ExampleQuestions
        preset={activePreset}
        onSelect={(q) => setPrefillQuestion(q)}
      />

      <AskPanel
        activePreset={activePreset}
        prefillQuestion={prefillQuestion}
        onQuestionClear={() => setPrefillQuestion(null)}
      />
    </div>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<MainPage />} />
          <Route
            path="/upload"
            element={
              <div className="max-w-3xl mx-auto px-4 py-8 flex flex-col gap-6">
                <div>
                  <h1 className="text-2xl font-bold text-white mb-1">Ingest documents</h1>
                  <p className="text-sm text-gray-400">
                    Add your own documentation via URL or PDF upload.
                  </p>
                </div>
                <UploadPanel />
              </div>
            }
          />
          <Route
            path="/dashboard"
            element={
              <div className="max-w-5xl mx-auto px-4 py-8 flex flex-col gap-6">
                <div>
                  <h1 className="text-2xl font-bold text-white mb-1">Analytics</h1>
                  <p className="text-sm text-gray-400">
                    Query patterns, source references, and similarity trends.
                  </p>
                </div>
                <Dashboard />
              </div>
            }
          />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>
      <div className="fixed bottom-3 right-4 text-right text-xs text-gray-600 select-none leading-tight">
        <div>Created by</div>
        <div className="font-medium">Eric Holt</div>
      </div>
    </div>
  );
}
