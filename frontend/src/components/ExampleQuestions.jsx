const EXAMPLES = {
  fastapi: [
    "How does dependency injection work and when should I use it over regular function parameters?",
    "What's the difference between async def and def route handlers and when does it matter?",
    "How do I implement OAuth2 password flow with JWT tokens?",
  ],
  langchain: [
    "What's the difference between a Chain and an Agent and when should I use each?",
    "How do I add memory to a conversational chain so it remembers previous messages?",
    "How does LangChain handle streaming responses from an LLM?",
  ],
  postgresql: [
    "What's the difference between an inner join and a left join and when would I use each?",
    "How do indexes work and how do I know when to add one?",
    "What is a CTE and how is it different from a subquery?",
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
