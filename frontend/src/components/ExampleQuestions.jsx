const EXAMPLES = {
  fastapi: [
    "How does dependency injection work and when should I use it over regular function parameters?",
    "What's the difference between async def and def route handlers and when does it matter?",
    "How do I implement OAuth2 password flow with JWT tokens?",
  ],
  sqlite: [
    "What's the difference between TEXT, REAL, and INTEGER storage classes in SQLite?",
    "How do I use a CTE and when is it better than a subquery?",
    "How does SQLite handle concurrent reads and writes?",
  ],
  requests: [
    "How do I send authentication headers with a request?",
    "What's the difference between params and data in a POST request?",
    "How do I handle timeouts and retries?",
  ],
};

export default function ExampleQuestions({ preset, onSelect }) {
  const questions = EXAMPLES[preset] || [];
  if (!questions.length) return null;

  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs text-gray-500 uppercase tracking-wide">Example questions</p>
      {questions.map((q) => (
        <button
          key={q}
          onClick={() => onSelect(q)}
          className="text-left text-sm text-gray-300 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 hover:border-cyan-600 hover:text-white transition-colors"
        >
          {q}
        </button>
      ))}
    </div>
  );
}
