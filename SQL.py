import sqlite3


def init_db():
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
