import sqlite3

conn = sqlite3.connect('subscriptions.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        group_id INTEGER,
        area_name TEXT
    )
''')
conn.commit()
conn.close()