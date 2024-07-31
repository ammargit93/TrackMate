from flask import *
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')
conn.commit()
conn.close()


def insert_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO Users (username, password) VALUES (?, ?)
        ''', (username, password))
        conn.commit()
        print('User inserted successfully!')
    except sqlite3.IntegrityError as e:
        print(f'Error: {e}')
    finally:
        res = cursor.execute('''select * from Users''')
        conn.close()


def find_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        users = cursor.execute('''select * from Users where username=? and password=?''', (username, password))
        user = users.fetchone()
        return user is not None
    finally:
        conn.close()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'signup':
            return redirect(url_for('signup'))
        elif action == 'login':
            return redirect(url_for('login'))
        else:
            flash('Invalid action!', 'danger')
            return redirect(url_for('home'))
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        insert_user(username, password)
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        res = find_user(username, password)
        print(res)
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)
