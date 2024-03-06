import sqlite3

conn = sqlite3.connect('bd.db')
c = conn.cursor()

c.executescript('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    value INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    link_name TEXT NOT NULL,
    original_link TEXT NOT NULL,
    generated_link TEXT NOT NULL UNIQUE,
    qr_code BLOB,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS click_statistic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link_id INTEGER NOT NULL,
    click_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_ip TEXT,
    device_info TEXT,
    city TEXT,
    gender TEXT CHECK (gender IN ('male', 'female', 'unknown')),
    FOREIGN KEY(link_id) REFERENCES link(id)
);
''')

c.execute('''
INSERT INTO user (username, email, password, is_admin)
VALUES (?, ?, ?, ?)
''', ('DUXA', 'N/A', "passwordissohard", True))

conn.commit()
conn.close()
print("База данных инициализирована.")
