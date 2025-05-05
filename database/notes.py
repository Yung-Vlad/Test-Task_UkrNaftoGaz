import sqlite3
from models.notes import NoteInternalModel, NoteUpdateInternalModel
from typing import Optional

from .general import DB_PATH


def add_note(note: NoteInternalModel, from_user: int) -> None:
    """
    Add new note to db
    :param note: all info about this note (header, content, tags)
    :param from_user: user's id who wants to get his notes
    """

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO notes (header, content, tags, created_time, from_user_id) VALUES (?, ?, ?, ?, ?)
        """, (note.header, note.text, note.tags, note.created_time, from_user))
        conn.commit()

        # Increment counter for creating notes
        cursor.execute("""
            UPDATE statistics SET count_creating_note = count_creating_note + 1 
            WHERE user_id = ? 
        """, (from_user,))
        conn.commit()

def get_all_notes(user_id: int, offset: int, limit: int, tags: Optional[str]) -> dict:
    """
    Getting all notes for users by his id
    :param user_id: user's id who want to get his notes
    :param offset: offset from the start of the available notes
    :param limit: count notes for 1 query
    :param tags: filter notes by tags
    """

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Query and parameters
        query = f"""
            SELECT * FROM notes WHERE from_user_id = ? OR id IN (SELECT note_id FROM accesses WHERE user_id = ?) 
            {"AND tags LIKE ? " if tags is not None else ""} ORDER BY id LIMIT ? OFFSET ?
        """
        params = [user_id, user_id, tags, limit, offset]

        # If tags is None then remove it from parameters
        if not tags:
            params.remove(tags)

        cursor.execute(query, params)

        data = cursor.fetchall()
        if not data:  # If nothing found
            return { "message": "No notes found!" }

        # Increase counter for reading notes
        cursor.execute("""
            UPDATE statistics SET count_reading_note = count_reading_note + ? 
            WHERE user_id = ? 
        """, (len(data), user_id))
        conn.commit()

        # Return dictionary in understandable format
        return { item[0]: { "header": item[1], "content": item[2], "tags": item[3], "from_user_id": item[4],
                            "created_time": item[5], "last_edit_time": item[6], "last_edit_user": item[7] }
                 for item in data }

def get_note_by_id(note_id: int, user_id: int) -> dict:
    """
    Get note by id for user if he has access for this note
    """

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM notes WHERE id = ? AND (from_user_id = ? OR 
            EXISTS (SELECT 1 FROM accesses WHERE note_id = ? AND user_id = ?))
        """, (note_id, user_id, note_id, user_id))

        data = cursor.fetchone()
        if not data:
            return { "message": f"Note not found or access denied!" }

        # Increment counter for reading notes
        cursor.execute("""
                            UPDATE statistics SET count_reading_note = count_reading_note + 1 
                            WHERE user_id = ? 
                        """, (user_id,))
        conn.commit()

        return { "id": data[0], "header": data[1], "content": data[2], "tags": data[3], "from_user_id": data[4],
                 "created_time": data[5], "last_edit_time": data[6], "last_edit_user": data[7] }

def delete_note_by_id(note_id: int, user_id: int) -> dict:
    """
    Delete note by id if user is owner this note
    """

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM notes WHERE id = ? AND from_user_id = ?
        """, (note_id, user_id))

        # If not exist note with :note_id or this user isn't owner this note
        if cursor.rowcount == 0:
            return { "message": "Note not found or access denied!" }

        # Delete all accesses for this note
        cursor.execute("""
            DELETE FROM accesses WHERE note_id = ?
        """, (note_id,))

        conn.commit()

        # Increment counter for deleting notes
        cursor.execute("""
                    UPDATE statistics SET count_deleting_note = count_deleting_note + 1 
                    WHERE user_id = ? 
                """, (user_id,))
        conn.commit()

        return { "message": "Note has been successfully deleted" }

def check_access(note_id: int, user_id: int) -> bool:
    """
    Check user access to note
    """

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM notes WHERE id = ? AND (from_user_id = ? OR 
            EXISTS (SELECT 1 FROM accesses WHERE note_id = ? AND user_id = ? AND permission = 2))
        """, (note_id, user_id, note_id, user_id))

        return bool(cursor.fetchone())

def update_note(note: NoteUpdateInternalModel) -> dict:
    """
    Update note in db after editing
    """

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notes SET header = ?, content = ?, tags = ?, last_edit_time = ?, last_edit_user = ? WHERE id = ?
        """, (note.header, note.text, note.tags, note.last_edit_time, note.id, note.last_edit_user))
        conn.commit()

        return { "message": "Note has successfully updated" }
