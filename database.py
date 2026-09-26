import sqlite3
from datetime import datetime, timedelta

DB_NAME = "doit.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT DEFAULT 'avatars/avatar1.png',
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_email TEXT,
            judul TEXT NOT NULL,
            kategori TEXT NOT NULL,
            tipe TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Belum',
            tanggal_selesai TEXT,
            deadline TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            nama_kategori TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN deadline TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE tasks ADD COLUMN user_email TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

def save_session(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions")
    cursor.execute("INSERT INTO sessions (email) VALUES (?)", (email,))
    conn.commit()
    conn.close()

def get_active_session():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM sessions LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def clear_session():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()

def register_user(nama, email, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("INSERT INTO users (nama, email, password, avatar, created_at) VALUES (?, ?, ?, 'avatars/avatar1.png', ?)", (nama, email, password, now_str))
        user_id = cursor.lastrowid

        default_cats = ["Sekolah", "Kuliah", "Pekerjaan", "Pribadi", "Kesehatan"]
        for cat in default_cats:
            cursor.execute("INSERT INTO categories (user_id, nama_kategori) VALUES (?, ?)", (user_id, cat))

        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama, email, password, COALESCE(avatar, 'avatars/avatar1.png'), COALESCE(created_at, '-') FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_email(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama, email, password, COALESCE(avatar, 'avatars/avatar1.png'), COALESCE(created_at, '-') FROM users WHERE email = ?", (email,))
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

def get_user_categories(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nama_kategori FROM categories WHERE user_id = ? ORDER BY nama_kategori ASC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_category(user_id, nama_kategori):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (user_id, nama_kategori) VALUES (?, ?)", (user_id, nama_kategori))
    conn.commit()
    conn.close()

def delete_category(cat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
    conn.commit()
    conn.close()

def get_tasks_by_user(user_id, tipe, sort_by="default", search_query=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = """
        SELECT id, user_id, judul, kategori, tipe, status, tanggal_selesai, deadline 
        FROM tasks 
        WHERE user_id = ? AND tipe = ? AND status = 'Belum'
    """
    params = [user_id, tipe]

    if search_query:
        query += " AND LOWER(judul) LIKE ?"
        params.append(f"%{search_query.lower()}%")

    if sort_by == "deadline":
        query += " ORDER BY CASE WHEN deadline IS NULL OR deadline = '' THEN 1 ELSE 0 END, deadline ASC"
    elif sort_by == "alphabet":
        query += " ORDER BY LOWER(judul) ASC"
    else:
        query += " ORDER BY id DESC"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_task(user_id, user_email, judul, kategori, tipe, deadline=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (user_id, user_email, judul, kategori, tipe, status, deadline) 
        VALUES (?, ?, ?, ?, ?, 'Belum', ?)
    """, (user_id, user_email, judul, kategori, tipe, deadline))
    conn.commit()
    conn.close()

def update_task(task_id, judul, kategori, deadline=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks 
        SET judul = ?, kategori = ?, deadline = ? 
        WHERE id = ?
    """, (judul, kategori, deadline, task_id))
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
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT id, judul, tipe, COALESCE(tanggal_selesai, '-') FROM tasks 
        WHERE user_id = ? AND status = 'Selesai' AND tanggal_selesai >= ?
        ORDER BY tanggal_selesai DESC, id DESC
    """, (user_id, seven_days_ago))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_completed_tasks_by_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, judul, tipe, COALESCE(tanggal_selesai, '-') FROM tasks 
        WHERE user_id = ? AND status = 'Selesai'
        ORDER BY tanggal_selesai DESC, id DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_user_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'Selesai'", (user_id,))
    completed = cursor.fetchone()[0]
    conn.close()
    return total, completed

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
    start_of_week = today - timedelta(days=today.weekday())
    
    days_map = [
        ("Sen", 0),
        ("Sel", 1),
        ("Rab", 2),
        ("Kam", 3),
        ("Jum", 4),
        ("Sab", 5),
        ("Min", 6)
    ]
    
    counts = []
    for day_name, offset in days_map:
        target_date = (start_of_week + timedelta(days=offset)).strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'Selesai' AND tanggal_selesai = ?", (user_id, target_date))
        cnt = cursor.fetchone()[0]
        counts.append((day_name, cnt))
        
    conn.close()
    return counts

def get_monthly_completed_counts(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    counts = []
    
    for i in range(3, -1, -1):
        start_date = (today - timedelta(days=(i * 7) + 6)).strftime("%Y-%m-%d")
        end_date = (today - timedelta(days=i * 7)).strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE user_id = ? AND status = 'Selesai' AND tanggal_selesai BETWEEN ? AND ?
        """, (user_id, start_date, end_date))
        cnt = cursor.fetchone()[0]
        week_name = f"Mng {4 - i}"
        counts.append((week_name, cnt))
        
    conn.close()
    return counts