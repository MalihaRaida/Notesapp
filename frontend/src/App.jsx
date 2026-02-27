import React, { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);

  async function refresh() {
    const res = await fetch(`${API_BASE}/notes`);
    const data = await res.json();
    setNotes(data);
  }

  useEffect(() => {
    refresh();
  }, []);

  async function addNote(e) {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content }),
      });
      if (!res.ok) throw new Error(await res.text());
      setTitle("");
      setContent("");
      await refresh();
    } finally {
      setLoading(false);
    }
  }

  async function deleteNote(id) {
    const res = await fetch(`${API_BASE}/notes/${id}`, { method: "DELETE" });
    if (res.status !== 204) {
      alert("Delete failed");
      return;
    }
    await refresh();
  }

  return (
    <div style={{ maxWidth: 720, margin: "40px auto", fontFamily: "system-ui" }}>
      <h1>Notes</h1>

      <form onSubmit={addNote} style={{ display: "grid", gap: 8, marginBottom: 20 }}>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Title"
          style={{ padding: 10, fontSize: 16 }}
        />
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write something..."
          rows={4}
          style={{ padding: 10, fontSize: 16 }}
        />
        <button disabled={loading} style={{ padding: 10, fontSize: 16 }}>
          {loading ? "Adding..." : "Add Note"}
        </button>
      </form>

      <div style={{ display: "grid", gap: 10 }}>
        {notes.map((n) => (
          <div
            key={n.id}
            style={{
              border: "1px solid #ddd",
              borderRadius: 10,
              padding: 12,
              display: "grid",
              gap: 6,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <strong>{n.title}</strong>
              <button onClick={() => deleteNote(n.id)}>Delete</button>
            </div>
            {n.content ? <div style={{ whiteSpace: "pre-wrap" }}>{n.content}</div> : null}
            <small style={{ opacity: 0.7 }}>
              Updated: {new Date(n.updated_at).toLocaleString()}
            </small>
          </div>
        ))}
        {notes.length === 0 ? <p>No notes yet.</p> : null}
      </div>
    </div>
  );
}