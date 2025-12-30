import React, { useState } from "react";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setLoading(true);
    setResponse("");
    setError(null);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: input }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Backend error ${res.status}: ${text}`);
      }

      const data = await res.json();

      if (!data.reply) {
        throw new Error("No reply field in response");
      }

      setResponse(data.reply);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to fetch");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>CS Tutor Bot</h1>

      <textarea
        placeholder="Ask a computer science question..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />

      <button onClick={sendMessage} disabled={loading}>
        {loading ? "Thinking..." : "Ask"}
      </button>

      {error && (
        <div className="error">
          ❌ {error}
        </div>
      )}

      {response && (
        <div className="response">
          <pre>{response}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
