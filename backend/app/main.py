import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from .model import NoteCreate, NoteUpdate

from .db import get_conn
from .schema import SCHEMA_SQL

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("AUTO_INIT_DB", "true").lower() == "true":
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
            conn.commit()
    yield

app = FastAPI(title="Notes API", lifespan=lifespan)

origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "time": datetime.now(timezone.utc).isoformat()}

@app.get("/notes")
def list_notes():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM notes ORDER BY updated_at DESC, id DESC;")
            return cur.fetchall()

@app.get("/notes/{note_id}")
def get_note(note_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM notes WHERE id = %s;", (note_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Note not found")
            return row

@app.post("/notes", status_code=201)
def create_note(payload: NoteCreate):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO notes (title, content) VALUES (%s, %s) RETURNING *;",
                (payload.title, payload.content),
            )
            row = cur.fetchone()
        conn.commit()
    return row

@app.patch("/notes/{note_id}")
def update_note(note_id: int, payload: NoteUpdate):
    fields = []
    vals = []
    if payload.title is not None:
        fields.append("title = %s")
        vals.append(payload.title)
    if payload.content is not None:
        fields.append("content = %s")
        vals.append(payload.content)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    vals.append(note_id)
    sql = f"UPDATE notes SET {', '.join(fields)} WHERE id = %s RETURNING *;"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(vals))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Note not found")
        conn.commit()
    return row

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM notes WHERE id = %s RETURNING id;", (note_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Note not found")
        conn.commit()
    return