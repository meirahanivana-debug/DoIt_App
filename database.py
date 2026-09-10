import sqlite3

def init_db():
    conn = sqlite3.connect('doit.db')
    cursor = conn.cursor()
    
    # Tabel Users untuk Login & Daftar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    
    # Tabel Tasks (ditambahkan column user_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT,
            type TEXT,
            status INTEGER DEFAULT 0,
            date_completed TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database SQLite dengan Multi-User berhasil disiapkan!")