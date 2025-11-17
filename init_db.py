"""Simple script to create the SQLite database and table."""
import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
# allow tests to override the DB path via TEST_DATABASE env var
DB = os.environ.get('TEST_DATABASE', os.path.join(BASE_DIR, 'database.db'))

def init_db():
    conn = sqlite3.connect(DB)
    with conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )

        # users table for simple session-based auth
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
            '''
        )

        # insert default admin user if not exists
        try:
            cur = conn.execute('SELECT id FROM users WHERE username = ?', ('admin',))
            if not cur.fetchone():
                from werkzeug.security import generate_password_hash
                pw = generate_password_hash('password')
                conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', pw))
        except Exception:
            pass

    conn.close()

if __name__ == '__main__':
    init_db()
    print('Initialized database at', DB)
