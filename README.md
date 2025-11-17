# Small Flask Full-Stack Demo App

This is a simple full-stack assignment project demonstrating Flask + SQLite + basic frontend.

Features
- Add contact (name, email, message) via a form
- Server-side validation and client-side validation
- SQLite database storing submissions
- Results page displays saved records in an HTML table

Run locally (Windows PowerShell)

1. Create a virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Initialize the database (creates `database.db`):

```powershell
python init_db.py
```

4. Run the app:

```powershell
python app.py
```

5. Open http://127.0.0.1:5000 in your browser.

Notes
- The app auto-creates the DB on first request if not present, but running `init_db.py` ensures the table exists.
- For production, change `app.config['SECRET_KEY']` and disable `debug=True`.

Optional extras not included
- Authentication and unit tests (can be added for extra credit).
