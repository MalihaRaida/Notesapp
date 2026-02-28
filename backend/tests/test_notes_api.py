import unittest
from uuid import uuid4

from fastapi import HTTPException

from app.db import get_conn
from app.main import create_note, delete_note, get_note, list_notes, update_note
from app.model import NoteCreate, NoteUpdate
from app.schema import SCHEMA_SQL


class NotesApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
            conn.commit()

    def setUp(self):
        self.created_note_ids = []

    def tearDown(self):
        if not self.created_note_ids:
            return

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM notes WHERE id = ANY(%s);",
                    (self.created_note_ids,),
                )
            conn.commit()

    def _create_note(self, title: str, content: str = "") -> dict:
        note = create_note(NoteCreate(title=title, content=content))
        self.created_note_ids.append(note["id"])
        return note

    def test_create_and_get_note(self):
        title = f"test-title-{uuid4()}"
        created = self._create_note(title=title, content="test-content")

        note = get_note(created["id"])
        self.assertEqual(note["id"], created["id"])
        self.assertEqual(note["title"], title)
        self.assertEqual(note["content"], "test-content")

    def test_list_notes_includes_new_note(self):
        created = self._create_note(title=f"test-list-{uuid4()}", content="list-content")

        notes = list_notes()
        note_ids = {note["id"] for note in notes}
        self.assertIn(created["id"], note_ids)

    def test_patch_note_updates_fields(self):
        created = self._create_note(
            title=f"test-update-{uuid4()}",
            content="before-update",
        )

        updated = update_note(
            created["id"],
            NoteUpdate(title="after-update", content="updated-content"),
        )
        self.assertEqual(updated["title"], "after-update")
        self.assertEqual(updated["content"], "updated-content")

    def test_patch_note_requires_payload_fields(self):
        created = self._create_note(title=f"test-empty-patch-{uuid4()}")

        with self.assertRaises(HTTPException) as context:
            update_note(created["id"], NoteUpdate())

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "No fields to update")

    def test_delete_note_removes_row(self):
        created = self._create_note(title=f"test-delete-{uuid4()}")

        delete_note(created["id"])
        self.created_note_ids.remove(created["id"])

        with self.assertRaises(HTTPException) as context:
            get_note(created["id"])

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Note not found")


if __name__ == "__main__":
    unittest.main()
