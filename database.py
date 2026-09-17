import sqlite3
from datetime import datetime, timedelta

DB_NAME = "doit.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabel Users (Termasuk kolom avatar)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT DEFAULT '🐶'
        )
    ''')
    
    # Tabel Tasks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            judul TEXT NOT NULL,
            kategori TEXT NOT NULL,
            tipe TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Belum',
            tanggal_selesai TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(nama, email, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (nama, email, password, avatar) VALUES (?, ?, ?, '🐶')", (nama, email, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama, email, password, COALESCE(avatar, '🐶') FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_profile(user_id, nama, email, avatar):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET nama = ?, email = ?, avatar = ? WHERE id = ?", (nama, email, avatar, user_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def update_user_password(user_id, new_password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
    conn.commit()
    conn.close()

def get_tasks_by_user(user_id, tipe):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, judul, kategori, tipe, status, tanggal_selesai 
        FROM tasks 
        WHERE user_id = ? AND tipe = ? AND status = 'Belum'
        ORDER BY id DESC
    """, (user_id, tipe))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_task(user_id, judul, kategori, tipe):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (user_id, judul, kategori, tipe, status) 
        VALUES (?, ?, ?, ?, 'Belum')
    """, (user_id, judul, kategori, tipe))
    conn.commit()
    conn.close()

def update_task_status(task_id, status):
    tgl = datetime.now().strftime("%Y-%m-%d") if status == "Selesai" else None
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ?, tanggal_selesai = ? WHERE id = ?", (status, tgl, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_completed_tasks_by_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, judul, tipe, COALESCE(tanggal_selesai, '-') FROM tasks 
        WHERE user_id = ? AND status = 'Selesai'
        ORDER BY id DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_completion_dates_by_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT tanggal_selesai FROM tasks 
        WHERE user_id = ? AND status = 'Selesai' AND tanggal_selesai IS NOT NULL
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    dates = []
    for r in rows:
        try:
            dates.append(datetime.strptime(r[0], "%Y-%m-%d").date())
        except Exception:
            pass
    return dates

def get_weekly_completed_counts(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    counts = []
    
    for i in range(6, -1, -1):
        target_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'Selesai' AND tanggal_selesai = ?", (user_id, target_date))
        cnt = cursor.fetchone()[0]
        day_name = (today - timedelta(days=i)).strftime("%a")
        counts.append((day_name, cnt))
        
    conn.close()
    return counts