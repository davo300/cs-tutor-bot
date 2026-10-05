import React, { useRef, useState } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

const suggestions = [
  { label: "Language operations", question: "Explain union and concatenation of two languages. Use mathematical notation." },
  { label: "Kleene closure", question: "Explain Kleene closure and positive closure. Include epsilon and mathematical notation." },
  { label: "Assignment 1", question: "According to Assignment 1, what makes a valid identifier?" },
];

function App() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const [askedQuestion, setAskedQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const sourceMatch = response.match(/\n\nSOURCE:\s*([^\n]+)\s*$/);
  const answer = sourceMatch ? response.slice(0, sourceMatch.index) : response;
  const sources = sourceMatch ? sourceMatch[1].split(/,\s*/) : [];

  const sendMessage = async () => {
    const question = input.trim();
    if (!question || loading) return;
    setLoading(true);
    setAskedQuestion(question);
    setResponse("");
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question }),
      });
      if (!res.ok) throw new Error(`The tutor couldn't answer right now (error ${res.status}). Please try again.`);
      const data = await res.json();
      if (typeof data.reply !== "string" || !data.reply.trim()) throw new Error("The tutor returned an empty answer. Please try again.");
      setResponse(data.reply);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Couldn't connect to the tutor. Check that the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="workspace">
      <header className="topbar">
        <a className="brand" href="/"><span className="brand-mark" aria-hidden="true">∩</span> CS Tutor <span className="brand-tag">COMP–2140</span></a>
        <span className="topbar-caption">Your course. A little clearer.</span>
      </header>
      <main>
        <section className="intro">
          <div className="eyebrow"><span /> THE COMPILERS STUDY ROOM</div>
          <h1>Make sense of<br />the <span>language.</span></h1>
          <p>From regular expressions to tiny languages. Explore your lectures and assignments, one question at a time.</p>
        </section>
        <div className="study-layout">
          <div className="study-main">
            <form className="composer" onSubmit={event => { event.preventDefault(); sendMessage(); }}>
              <div className="panel-heading"><label htmlFor="course-question">What are you working on?</label><span className="small-label">01 / ASK</span></div>
              <textarea id="course-question" aria-label="Course question" ref={inputRef}
                placeholder="e.g. How is Kleene closure different from positive closure?"
                value={input} disabled={loading} onChange={event => setInput(event.target.value)}
                onKeyDown={event => { if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) { event.preventDefault(); sendMessage(); } }} />
              <div className="composer-footer"><span>Include an assignment number for a specific question.</span><button className="ask-button" type="submit" disabled={loading || !input.trim()}>{loading ? "Thinking…" : "Ask"}<span aria-hidden="true">↗</span></button></div>
            </form>
            <div className="suggestions"><span>TRY A TOPIC</span>{suggestions.map(item => <button type="button" key={item.label} disabled={loading} onClick={() => { setInput(item.question); inputRef.current?.focus(); }}>{item.label}<span aria-hidden="true">↗</span></button>)}</div>
            {error && <div className="error" role="alert">{error}</div>}
            <section className="answer-panel" aria-label="Tutor answer" aria-busy={loading}>
              <div className="panel-heading"><h2>{response ? "Let's break it down" : "A little clarity, coming up"}</h2><span className="small-label">02 / UNDERSTAND</span></div>
              {loading ? <div className="loading-state" role="status"><span className="loading-dot" /> Finding relevant course material and preparing your explanation…</div> : response ? <>
                <div className="question-echo"><span>YOUR QUESTION</span><p>{askedQuestion}</p></div>
                <div className="response"><ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>{answer}</ReactMarkdown></div>
                {sources.length > 0 && <footer className="source-footer"><h3>COURSE REFERENCES</h3><ul>{sources.map(source => <li key={source}><span aria-hidden="true">▤</span>{source}</li>)}</ul></footer>}
              </> : <div className="empty-state"><div className="empty-symbol" aria-hidden="true">L* = &#123; ε, … &#125;</div><h3>Start with a question.</h3><p>Your explanation will appear here, with mathematical notation and references to the course material.</p></div>}
            </section>
          </div>
          <aside className="study-notes">
            <div className="note-number">FIELD NOTES / 2140</div><h2>Small questions.<br />Better understanding.</h2>
            <p>This is your space to unpack the concepts behind the code.</p>
            <div className="note-divider" />
            <h3>A good place to start</h3>
            <ul><li><span>01</span>Ask for a definition or compare two concepts.</li><li><span>02</span>Request notation or an example when it helps.</li><li><span>03</span>Check the cited pages in your course material.</li></ul>
            <div className="notation-card"><span>THE LANGUAGE OF LANGUAGES</span><div aria-hidden="true">∪ &nbsp; ∩ &nbsp; ε &nbsp; Σ</div><p>Sets, strings, and the rules that connect them.</p></div>
          </aside>
        </div>
      </main>
      <footer className="page-footer"><span>COMP–2140 · Course companion</span><span>Built for understanding.</span></footer>
    </div>
  );
}
export default App;
