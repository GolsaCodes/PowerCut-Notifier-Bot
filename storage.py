import sqlite3

DB_PATH = 'subscriptions.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            group_id INTEGER,
            area_name TEXT,
            PRIMARY KEY (group_id, area_name)
        )
    ''')
    conn.commit()
    conn.close()

def load_subscriptions(group_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT area_name FROM subscriptions WHERE group_id = ?', (group_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def load_all_subscriptions():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT group_id, area_name FROM subscriptions')
    rows = cursor.fetchall()
    conn.close()

    subscriptions = {}
    for group_id, area_name in rows:
        subscriptions.setdefault(group_id, []).append(area_name)
    return subscriptions

def save_subscription(group_id, area_name):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO subscriptions (group_id, area_name) VALUES (?, ?)', (group_id, area_name))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def remove_subscription(group_id, area_name):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subscriptions WHERE group_id = ? AND area_name = ?', (group_id, area_name))
    changes = cursor.rowcount
    conn.commit()
    conn.close()
    return changes > 0