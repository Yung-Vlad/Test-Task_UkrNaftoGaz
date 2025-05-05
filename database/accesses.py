import sqlite3
from models.users import AccessInternalModel, AccessModel

from .general import DB_PATH
from .users import get_email
from secure.notification import notify


def set_permission(access: AccessInternalModel, owner_id: int) -> dict:
    if not check_is_owner_of_note(owner_id, access.note_id):
        return { "message": "This action can only be performed by owner of note" }

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO accesses (note_id, user_id, permission) VALUES (?, ?, ?)
        """, (access.note_id, access.user_id, access.permission))

        if cursor.rowcount == 0:  # If ignore
            return { "message": "This user already has access to this note" }

        conn.commit()

        ##### Send email
        permission = "read" if access.permission == 1 else "read & write"
        notify(get_email(access.user_id),
               make_notification_text({ "email": get_email(owner_id),
                                        "note_id": access.note_id,
                                        "permission": f"Gave access to {permission}" }))

        return { "message": "User successfully gained access" }

def delete_permission(access: AccessModel, owner_id: int) -> dict:
    if not check_is_owner_of_note(owner_id, access.note_id):
        return { "message": "This action can only be performed by owner of note" }

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM accesses WHERE note_id = ? AND user_id = ?
        """, (access.note_id, access.user_id))

        if cursor.rowcount == 0:  # If user doesn't have access to this note
            return { "message": "This user doesn't have access to this note" }

        conn.commit()

        ##### Send email
        notify(get_email(access.user_id), make_notification_text({ "email": get_email(owner_id),
                                                                       "note_id": access.note_id,
                                                                       "permission": "Take away access" }))

        return { "message": "User successfully lost access" }

def edit_permission(access: AccessInternalModel, owner_id: int) -> dict:
    if not check_is_owner_of_note(owner_id, access.note_id):
        return { "message": "This action can only be performed by owner of note" }

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT permission FROM accesses WHERE note_id = ? AND user_id = ?
        """, (access.note_id, access.user_id))

        row = cursor.fetchone()
        if not row:
            return {"message": "This user doesn't have access to this note"}
        elif row[0] == access.permission:  # If not changed
            return {"message": "You select the same rights as user had"}

        cursor.execute("""
            UPDATE accesses SET permission = ? WHERE note_id = ? AND user_id = ?
        """, (access.permission, access.note_id, access.user_id))

        conn.commit()

        ##### Send email
        permission = "read" if access.permission == 1 else "read & write"
        notify(get_email(access.user_id),
               make_notification_text({ "email": get_email(owner_id),
                                        "note_id": access.note_id,
                                        "permission": f"Change your access to {permission}" }))

        return { "message": "Rights successfully changed" }

def check_is_owner_of_note(user_id: int, note_id: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM notes WHERE id = ? AND from_user_id = ?
        """, (note_id, user_id))

        if not cursor.fetchone():
            return False

        return True

def make_notification_text(data: dict) -> str:
    """
    Build message string to send
    """

    note_id = data["note_id"]
    message = (f"From user: {data['email']}\nID note: {note_id}\n"
            f"Permission: {data['permission']}\nLink: https://NotesAPI/notes/{note_id}")  # (Conditional address)

    return message
