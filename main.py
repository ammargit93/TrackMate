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
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Subjects (
        sub_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sub_name TEXT UNIQUE NOT NULL,
        total_lec integer NOT NULL default 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Attendance (
        att_id INTEGER PRIMARY KEY AUTOINCREMENT,
        id integer NOT NULL,
        sub_id integer NOT NULL,
        lec_attended integer not null default 0,
        foreign key (id) references Users (id),
        foreign key (sub_id) references subjects (sub_id)
 
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
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        user_id = cursor.execute('''select id from Users where username=? and password=?''', (username, password))
        session['username'] = username
        session['user_id'] = user_id.fetchall()[0][0]
        return redirect(url_for('dashboard'))

    return render_template('login.html')


# def get_user_id(username, password):
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     user_id = cursor.execute('''select id from Users where username=? and password=?''', (username, password))
#     conn.close()
#     return user_id.fetchall()[0][0]
#
#
# def get_subject_id(subject_name, total_lec):
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     sub_id = cursor.execute('''select sub_id from Subjects where subname=? and total_lec=?''',
#                             (subject_name, total_lec))
#     conn.close()
#     return sub_id.fetchall()[0][0]


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        total_lec = request.form.get('total_lectures')
        lec_attended = request.form.get('lectures_attended')
        print(subject_name, total_lec, lec_attended)
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO Subjects (sub_name, total_lec) VALUES (?, ?)''', (subject_name, total_lec))
            sub_id = cursor.execute('''select sub_id from Subjects where sub_name=? and total_lec=?''',
                                    (subject_name, total_lec))
            a = cursor.execute('''INSERT INTO Attendance (id,sub_id,lec_attended) VALUES (?, ?, ?)''',
                           (session['user_id'], sub_id.fetchall()[0][0], lec_attended))
            conn.commit()
            print(a.fetchall())
        except sqlite3.IntegrityError as e:
            print(f'Error: {e}')
        finally:
            conn.close()

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    record = cur.execute(
            '''
                   select Users.username,Subjects.sub_name,Subjects.total_lec, Attendance.lec_attended,
                   ROUND((Attendance.lec_attended * 100.0 / Subjects.total_lec), 2) AS attendance_percentage
                   from Attendance join Users on Attendance.id = Users.id
                   join Subjects on Attendance.sub_id = Subjects.sub_id  
            ''')

    return render_template('dashboard.html', record=record)


if __name__ == '__main__':
    app.run(debug=True)
