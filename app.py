from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(BASE_DIR, 'database.db')


def get_db_connection():
    db_path = app.config.get('DATABASE', DATABASE)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
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
    conn.close()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-change-me'

# allow overriding the database path (useful for tests)
app.config['DATABASE'] = os.environ.get('TEST_DATABASE', DATABASE)


try:
    init_db()
except Exception as e:
    print('DB init error:', e)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['GET', 'POST'])
def add():
    # require login to add
    if not session.get('user'):
        flash('Please log in to add contacts.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        error = None
        if not name:
            error = 'Name is required.'
        elif not email:
            error = 'Email is required.'
        elif not message:
            error = 'Message is required.'

        if error:
            return render_template('add.html', error=error, form={'name': name, 'email': email, 'message': message})

        try:
            conn = get_db_connection()
            with conn:
                conn.execute('INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)', (name, email, message))
            flash('Entry added successfully.', 'success')
            return redirect(url_for('results'))
        except sqlite3.Error as e:
            return render_template('add.html', error='Database error: ' + str(e), form={'name': name, 'email': email, 'message': message})

    return render_template('add.html')


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Username and password required.', 'danger')
            return render_template('login.html')

        try:
            conn = get_db_connection()
            user = conn.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
        except sqlite3.Error as e:
            flash('Database error: ' + str(e), 'danger')
            return render_template('login.html')

        from werkzeug.security import check_password_hash

        if user and check_password_hash(user['password_hash'], password):
            session['user'] = user['username']
            flash('Logged in as ' + user['username'], 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/results')
def results():
    try:
        conn = get_db_connection()
        rows = conn.execute('SELECT id, name, email, message, created FROM contacts ORDER BY created DESC').fetchall()
        conn.close()
    except sqlite3.Error as e:
        rows = []
        flash('Could not read from database: ' + str(e), 'danger')

    return render_template('results.html', rows=rows)


if __name__ == '__main__':
    app.run(debug=True)
