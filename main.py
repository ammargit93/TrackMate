from flask import *
from SQL import init_db, find_user, insert_user
import sqlite3
from api import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

init_db()


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
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        user_id = cursor.execute('''select id from Users where username=? and password=?''', (username, password))
        session['username'] = username
        session['user_id'] = user_id.fetchall()[0][0]
        conn.close()
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST' and 'subject_id' not in request.form:
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


@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    if request.method == 'POST':
        s_name = request.form.get('subject_id')
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('''update Subjects set total_lec=total_lec+1 where sub_name=?''', (s_name,))
        conn.commit()
        sid = cur.execute('''select sub_id from Subjects where sub_name=?''', (s_name,))
        conn.commit()
        cur.execute('''update Attendance set lec_attended=lec_attended+1 where sub_id=?''', (sid.fetchall()[0][0],))
        conn.commit()
    return redirect('dashboard')


@app.route('/delete_subject', methods=['GET', 'POST'])
def delete_subject():
    if request.method == 'POST':
        s_name = request.form.get('subject_id')
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        sid = cur.execute('''select sub_id from Subjects where sub_name=?''', (s_name,))
        conn.commit()

        cur.execute('''delete from Subjects where sub_name=?''', (s_name,))
        conn.commit()

        print(s_name, sid.fetchone())
        cur.execute('''delete from Attendance where sub_id=?''', (sid.fetchone(),))
        conn.commit()
    return redirect('dashboard')


if __name__ == '__main__':
    app.run(debug=True)
