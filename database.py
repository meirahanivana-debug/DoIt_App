import datetime
import sqlite3


def init_db():
  conn = sqlite3.connect("doit.db")
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            category TEXT,
            type TEXT,
            status TEXT DEFAULT 'Belum',
            date_completed TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

  conn.commit()
  conn.close()


def register_user(nama, email, password):
  try:
    conn = sqlite3.connect("doit.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (nama, email, password),
    )
    conn.commit()
    conn.close()
    return True
  except sqlite3.IntegrityError:
    return False


def verify_user(email, password):
  conn = sqlite3.connect("doit.db")
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, name, email FROM users WHERE email = ? AND password = ?",
      (email, password),
  )
  user = cursor.fetchone()
  conn.close()
  return user


def add_task(user_id, judul, kategori, tipe):
  conn = sqlite3.connect("doit.db")
  cursor = conn.cursor()
  tanggal = datetime.datetime.now().strftime("%Y-%m-%d")
  cursor.execute(
      """
        INSERT INTO tasks (user_id, title, category, type, status, date_completed)
        VALUES (?, ?, ?, ?, 'Belum', ?)
    """,
      (user_id, judul, kategori, tipe, tanggal),
  )
  conn.commit()
  conn.close()


def get_tasks_by_user(user_id, tipe):
  conn = sqlite3.connect("doit.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        SELECT id, user_id, title, category, type, status, date_completed 
        FROM tasks WHERE user_id = ? AND type = ? AND status = 'Belum'
    """,
      (user_id, tipe),
  )
  tasks = cursor.fetchall()
  conn.close()
  return tasks


def update_task_status(task_id, status):
  conn = sqlite3.connect("doit.db")
  cursor = conn.cursor()
  cursor.execute(
      "UPDATE tasks SET status = ? WHERE id = ?",
      (
          status,
          task_id,
      ),
  )
  conn.commit()
  conn.close()


def delete_task(task_id):
  conn = sqlite3.connect("doit.db")
  cursor = conn.cursor()
  cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
  conn.commit()
  conn.close()


def get_completed_tasks_by_user(user_id):
  conn = sqlite3.connect("doit.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        SELECT title, type, date_completed FROM tasks 
        WHERE user_id = ? AND status = 'Selesai' ORDER BY id DESC
    """,
      (user_id,),
  )
  history = cursor.fetchall()
  conn.close()
  return history


def get_completion_dates_by_user(user_id):
  conn = sqlite3.connect("doit.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        SELECT DISTINCT date_completed FROM tasks 
        WHERE user_id = ? AND status = 'Selesai'
    """,
      (user_id,),
  )
  rows = cursor.fetchall()
  conn.close()

  dates = set()
  for row in rows:
    try:
      if row[0]:
        d = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
        dates.add(d)
    except:
      pass
  return dates


if __name__ == "__main__":
  init_db()
  print("Database berhasil disiapkan!")