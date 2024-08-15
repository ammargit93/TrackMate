import sqlite3


conn = sqlite3.connect('database.db')
cur = conn.cursor()
a = cur.execute('''select * from Users''')
conn.commit()
print(a.fetchall())


