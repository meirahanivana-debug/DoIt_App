from datetime import datetime, timedelta
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.textfield import MDTextField

import database


class LoginScreen(Screen):

  def do_login(self):
    email = self.ids.email_input.text.strip()
    password = self.ids.password_input.text.strip()

    if not email or not password:
      self.show_dialog("Peringatan", "Email dan Password wajib diisi!")
      return

    user = database.verify_user(email, password)
    if user:
      app = MDApp.get_running_app()
      app.current_user_id = user[0]
      app.current_user_nama = user[1]
      app.current_user_email = user[2]

      self.manager.get_screen("main").setup_user_data()
      self.manager.current = "main"

      self.ids.email_input.text = ""
      self.ids.password_input.text = ""
    else:
      self.show_dialog("Gagal Login", "Email atau Password salah!")

  def show_dialog(self, title, text):
    dialog = MDDialog(
        title=title,
        text=text,
        buttons=[
            MDFlatButton(
                text="OK",
                on_release=lambda x: dialog.dismiss(),
                theme_text_color="Custom",
                text_color=(0.12, 0.53, 0.90, 1),
            )
        ],
    )
    dialog.open()


class RegisterScreen(Screen):

  def do_register(self):
    nama = self.ids.reg_nama_input.text.strip()
    email = self.ids.reg_email_input.text.strip()
    password = self.ids.reg_password_input.text.strip()

    if not nama or not email or not password:
      self.show_dialog("Peringatan", "Semua kolom wajib diisi!")
      return

    success = database.register_user(nama, email, password)
    if success:
      dialog = MDDialog(
          title="Berhasil",
          text="Akun berhasil dibuat! Silakan login.",
          buttons=[
              MDFlatButton(
                  text="OK",
                  on_release=lambda x: self.finish_register(dialog),
                  theme_text_color="Custom",
                  text_color=(0.12, 0.53, 0.90, 1),
              )
          ],
      )
      dialog.open()
    else:
      self.show_dialog("Gagal", "Email sudah terdaftar!")

  def finish_register(self, dialog):
    dialog.dismiss()
    self.ids.reg_nama_input.text = ""
    self.ids.reg_email_input.text = ""
    self.ids.reg_password_input.text = ""
    self.manager.current = "login"

  def show_dialog(self, title, text):
    dialog = MDDialog(
        title=title,
        text=text,
        buttons=[
            MDFlatButton(
                text="OK",
                on_release=lambda x: dialog.dismiss(),
                theme_text_color="Custom",
                text_color=(0.12, 0.53, 0.90, 1),
            )
        ],
    )
    dialog.open()


class MainScreen(Screen):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.current_filter = "Tugas"
    self.dialog = None

  def setup_user_data(self):
    app = MDApp.get_running_app()
    self.ids.greeting_label.text = f"Selamat Pagi, {app.current_user_nama}!"
    self.ids.profile_nama.text = app.current_user_nama
    self.ids.profile_email.text = app.current_user_email
    self.ids.date_label.text = datetime.now().strftime("%d %b %Y")

    self.load_tasks()
    self.load_history()
    self.update_streak()

  def switch_filter(self, filter_type):
    self.current_filter = filter_type
    if filter_type == "Tugas":
      self.ids.btn_tugas.md_bg_color = (0.12, 0.53, 0.90, 1)
      self.ids.btn_tugas.text_color = (1, 1, 1, 1)
      self.ids.btn_kebiasaan.md_bg_color = (0.85, 0.88, 0.92, 1)
      self.ids.btn_kebiasaan.text_color = (0.3, 0.3, 0.3, 1)
    else:
      self.ids.btn_kebiasaan.md_bg_color = (0.12, 0.53, 0.90, 1)
      self.ids.btn_kebiasaan.text_color = (1, 1, 1, 1)
      self.ids.btn_tugas.md_bg_color = (0.85, 0.88, 0.92, 1)
      self.ids.btn_tugas.text_color = (0.3, 0.3, 0.3, 1)
    self.load_tasks()

  def load_tasks(self):
    self.ids.task_list.clear_widgets()
    app = MDApp.get_running_app()
    tasks = database.get_tasks_by_user(
        app.current_user_id, self.current_filter
    )

    for task in tasks:
      t_id, _, judul, kategori, tipe, status, _ = task

      card = MDCard(
          size_hint=(1, None),
          height="64dp",
          elevation=1,
          radius=[12],
          padding=["12dp", "8dp", "12dp", "8dp"],
      )

      layout = MDBoxLayout(orientation="horizontal", spacing="10dp")

      chk_btn = MDRaisedButton(
          text="✓",
          size_hint=(None, None),
          size=("36dp", "36dp"),
          md_bg_color=(0.2, 0.7, 0.3, 1),
      )
      chk_btn.bind(on_release=lambda x, tid=t_id: self.mark_done(tid))

      text_box = MDBoxLayout(orientation="vertical")
      text_box.add_widget(
          MDLabel(
              text=judul,
              bold=True,
              font_style="Subtitle2",
              theme_text_color="Primary",
          )
      )
      text_box.add_widget(
          MDLabel(
              text=f"Kategori: {kategori}",
              font_style="Caption",
              theme_text_color="Secondary",
          )
      )

      del_btn = MDRaisedButton(
          text="✕",
          size_hint=(None, None),
          size=("36dp", "36dp"),
          md_bg_color=(0.9, 0.2, 0.2, 1),
      )
      del_btn.bind(on_release=lambda x, tid=t_id: self.delete_task(tid))

      layout.add_widget(chk_btn)
      layout.add_widget(text_box)
      layout.add_widget(del_btn)

      card.add_widget(layout)
      self.ids.task_list.add_widget(card)

  def mark_done(self, task_id):
    database.update_task_status(task_id, "Selesai")
    self.load_tasks()
    self.load_history()
    self.update_streak()

  def delete_task(self, task_id):
    database.delete_task(task_id)
    self.load_tasks()

  def load_history(self):
    self.ids.history_list.clear_widgets()
    app = MDApp.get_running_app()
    history = database.get_completed_tasks_by_user(app.current_user_id)

    for h in history:
      judul, tipe, tgl = h
      item = OneLineIconListItem(text=f"{judul} ({tgl})")
      self.ids.history_list.add_widget(item)

  def update_streak(self):
    app = MDApp.get_running_app()
    dates = database.get_completion_dates_by_user(app.current_user_id)
    if not dates:
      self.ids.streak_label.text = "0 Hari Beruntun"
      return

    streak = 0
    today = datetime.now().date()
    check_date = today

    if check_date not in dates and (check_date - timedelta(days=1)) in dates:
      check_date = today - timedelta(days=1)

    while check_date in dates:
      streak += 1
      check_date -= timedelta(days=1)

    self.ids.streak_label.text = f"{streak} Hari Beruntun"

  def show_add_task_dialog(self):
    self.input_judul = MDTextField(hint_text="Nama Tugas / Kebiasaan")
    self.input_kategori = MDTextField(
        hint_text="Kategori (cth: Sekolah, Pribadi)"
    )

    content = MDBoxLayout(
        orientation="vertical",
        spacing="12dp",
        size_hint_y=None,
        height="120dp",
    )
    content.add_widget(self.input_judul)
    content.add_widget(self.input_kategori)

    self.dialog = MDDialog(
        title=f"Tambah {self.current_filter}",
        type="custom",
        content_cls=content,
        buttons=[
            MDFlatButton(
                text="BATAL", on_release=lambda x: self.dialog.dismiss()
            ),
            MDRaisedButton(
                text="SIMPAN",
                md_bg_color=(0.12, 0.53, 0.90, 1),
                on_release=lambda x: self.save_task(),
            ),
        ],
    )
    self.dialog.open()

  def save_task(self):
    judul = self.input_judul.text.strip()
    kategori = self.input_kategori.text.strip()
    if not kategori:
      kategori = "Umum"

    if judul:
      app = MDApp.get_running_app()
      database.add_task(
          app.current_user_id, judul, kategori, self.current_filter
      )
      self.dialog.dismiss()
      self.load_tasks()

  def do_logout(self):
    app = MDApp.get_running_app()
    app.current_user_id = None
    app.current_user_nama = ""
    app.current_user_email = ""
    self.manager.current = "login"


class DoItApp(MDApp):

  def build(self):
    self.theme_cls.primary_palette = "Blue"
    self.current_user_id = None
    self.current_user_nama = ""
    self.current_user_email = ""

    database.init_db()
    return Builder.load_file("doit.kv")


if __name__ == "__main__":
  DoItApp().run()