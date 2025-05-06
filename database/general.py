import sqlite3, os
from dotenv import load_dotenv


load_dotenv()
DB_PATH = os.getenv("DB_PATH")

def init_db() -> None:
    """
    Initialization db: Create db and tables (if not exists yet)
    """

    check_db_dir()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Table users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                public_key TEXT UNIQUE NOT NULL
            );
        """)

        # Table notes
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        header TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags TEXT,
                        aes_key TEXT UNIQUE NOT NULL,
                        from_user_id INTEGER NOT NULL,
                        created_time TEXT NOT NULL,
                        last_edit_time TEXT,
                        last_edit_user INTEGER,
                        FOREIGN KEY (from_user_id) REFERENCES users(id)
                    );
                """)

        # Table statistics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                user_id INTEGER NOT NULL,
                count_creating_note INTEGER NOT NULL,
                count_reading_note INTEGER NOT NULL,
                count_deleting_note INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)

        # Table accesses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accesses (
                note_id INTEGER,
                user_id INTEGER,
                permission INTEGER NOT NULL,
                key TEXT UNIQUE NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                PRIMARY KEY (note_id, user_id)
            );
        """)

        conn.commit()

def check_existing_email(email: str) -> bool:
    """
    Checking if email is already registered
    """

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM users WHERE email = ?
        """, (email, ))

        user = cursor.fetchone()
        if user:
            return True

        return False

def check_db_dir() -> None:
    if not os.path.exists("db"):
        os.mkdir("db")
