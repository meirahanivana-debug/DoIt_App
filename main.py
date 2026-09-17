import database
from datetime import datetime, timedelta

# Konfigurasi Ukuran Layar HP Android
import kivy
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu


class LoginScreen(Screen):
    def toggle_password_visibility(self, button_icon):
        password_input = self.ids.password_input
        if password_input.password:
            password_input.password = False
            button_icon.icon = "eye"
        else:
            password_input.password = True
            button_icon.icon = "eye-off"

    def do_login(self):
        try:
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
                app.current_user_password = user[3]
                app.current_user_avatar = user[4] if len(user) > 4 and user[4] else "account"

                self.manager.get_screen("main").setup_user_data()
                self.manager.current = "main"

                self.ids.email_input.text = ""
                self.ids.password_input.text = ""
            else:
                self.show_dialog("Gagal Login", "Email atau Password salah!")
        except Exception as e:
            self.show_dialog("Error", f"Terjadi kesalahan: {str(e)}")

    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss(),
                    theme_text_color="Custom",
                    text_color=(0.12, 0.53, 0.90, 1)
                )
            ]
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
                        text_color=(0.12, 0.53, 0.90, 1)
                    )
                ]
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
                    text_color=(0.12, 0.53, 0.90, 1)
                )
            ]
        )
        dialog.open()


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_filter = "Tugas"
        self.dialog = None
        self.category_menu = None

    def setup_user_data(self):
        app = MDApp.get_running_app()
        self.ids.greeting_label.text = f"Selamat Pagi, {app.current_user_nama}!"
        self.ids.profile_nama.text = app.current_user_nama
        self.ids.profile_email.text = app.current_user_email
        self.ids.profile_avatar_icon.icon = app.current_user_avatar if app.current_user_avatar else "account"
        self.ids.profile_info_email.text = app.current_user_email
        self.ids.profile_info_nama.text = app.current_user_nama
        self.ids.date_label.text = datetime.now().strftime("%d %b %Y")

        self.load_tasks()
        self.load_history()
        self.update_streak()
        self.load_weekly_chart()

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
        tasks = database.get_tasks_by_user(app.current_user_id, self.current_filter)

        for task in tasks:
            try:
                t_id = task[0]
                judul = task[2]
                kategori = task[3]

                card = MDCard(
                    size_hint=(1, None),
                    height="60dp",
                    elevation=1,
                    radius=[12],
                    padding=["10dp", "4dp", "10dp", "4dp"]
                )

                layout = MDBoxLayout(orientation="horizontal", spacing="10dp", pos_hint={"center_y": 0.5})

                chk_btn = MDIconButton(
                    icon="checkbox-blank-outline",
                    theme_icon_color="Custom",
                    icon_color=(0.5, 0.5, 0.5, 1),
                    pos_hint={"center_y": 0.5}
                )
                chk_btn.bind(on_release=lambda x, tid=t_id: self.mark_done(tid))

                text_box = MDBoxLayout(orientation="vertical", pos_hint={"center_y": 0.5})
                text_box.add_widget(MDLabel(text=str(judul), bold=True, font_style="Subtitle2", theme_text_color="Primary"))
                text_box.add_widget(MDLabel(text=f"Kategori: {kategori}", font_style="Caption", theme_text_color="Secondary"))

                del_btn = MDIconButton(
                    icon="trash-can-outline",
                    theme_icon_color="Custom",
                    icon_color=(0.9, 0.2, 0.2, 1),
                    pos_hint={"center_y": 0.5}
                )
                del_btn.bind(on_release=lambda x, tid=t_id: self.delete_task(tid))

                layout.add_widget(chk_btn)
                layout.add_widget(text_box)
                layout.add_widget(del_btn)

                card.add_widget(layout)
                self.ids.task_list.add_widget(card)
            except Exception:
                continue

    def mark_done(self, task_id):
        database.update_task_status(task_id, "Selesai")
        self.load_tasks()
        self.load_history()
        self.update_streak()
        self.load_weekly_chart()

    def delete_task(self, task_id):
        database.delete_task(task_id)
        self.load_tasks()

    def load_history(self):
        self.ids.history_list.clear_widgets()
        app = MDApp.get_running_app()
        history = database.get_completed_tasks_by_user(app.current_user_id)

        for h in history:
            try:
                t_id = h[0]
                judul = h[1]
                tgl = h[3] if len(h) >= 4 else "-"

                card = MDCard(
                    size_hint=(1, None),
                    height="56dp",
                    elevation=1,
                    radius=[10],
                    padding=["10dp", "4dp", "10dp", "4dp"],
                    md_bg_color=(0.96, 0.98, 1, 1)
                )

                layout = MDBoxLayout(orientation="horizontal", spacing="10dp", pos_hint={"center_y": 0.5})

                icon_done = MDIconButton(
                    icon="check-circle",
                    theme_icon_color="Custom",
                    icon_color=(0.2, 0.7, 0.3, 1),
                    pos_hint={"center_y": 0.5}
                )

                text_box = MDBoxLayout(orientation="vertical", pos_hint={"center_y": 0.5})
                text_box.add_widget(MDLabel(text=str(judul), bold=True, font_style="Body2", theme_text_color="Primary"))
                text_box.add_widget(MDLabel(text=f"Selesai pada: {tgl}", font_style="Caption", theme_text_color="Secondary"))

                del_btn = MDIconButton(
                    icon="delete-outline",
                    theme_icon_color="Custom",
                    icon_color=(0.8, 0.3, 0.3, 1),
                    pos_hint={"center_y": 0.5}
                )
                del_btn.bind(on_release=lambda x, tid=t_id: self.delete_history(tid))

                layout.add_widget(icon_done)
                layout.add_widget(text_box)
                layout.add_widget(del_btn)

                card.add_widget(layout)
                self.ids.history_list.add_widget(card)
            except Exception:
                continue

    def delete_history(self, task_id):
        database.delete_task(task_id)
        self.load_history()
        self.update_streak()
        self.load_weekly_chart()

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

    def load_weekly_chart(self):
        self.ids.chart_container.clear_widgets()
        app = MDApp.get_running_app()
        weekly_data = database.get_weekly_completed_counts(app.current_user_id)

        for day, cnt in weekly_data:
            col = MDBoxLayout(orientation="vertical", spacing="4dp", alignment_vertical="bottom")

            val_label = MDLabel(text=str(cnt), font_style="Caption", halign="center", theme_text_color="Secondary", size_hint_y=None, height="14dp")

            # Perhitungan tinggi grafik dinamis berbasis dp (8dp per tugas selesai)
            calculated_height = max(10, min(100, cnt * 8))
            
            bar_card = MDCard(
                size_hint=(None, None),
                width="24dp",
                height=f"{calculated_height}dp",
                md_bg_color=(0.12, 0.53, 0.90, 0.85) if cnt > 0 else (0.85, 0.88, 0.92, 1),
                radius=[4, 4, 0, 0],
                pos_hint={"center_x": 0.5}
            )

            day_label = MDLabel(text=day, font_style="Caption", halign="center", bold=True, theme_text_color="Primary", size_hint_y=None, height="14dp")

            col.add_widget(val_label)
            col.add_widget(bar_card)
            col.add_widget(day_label)

            self.ids.chart_container.add_widget(col)

    def show_add_task_dialog(self):
        self.input_judul = MDTextField(hint_text="Nama Tugas / Kebiasaan")
        self.input_kategori = MDTextField(
            hint_text="Pilih atau Ketik Kategori",
            text="Sekolah"
        )
        
        btn_drop = MDIconButton(
            icon="menu-down",
            pos_hint={"center_y": 0.5}
        )
        btn_drop.bind(on_release=self.open_category_menu)

        kat_box = MDBoxLayout(orientation="horizontal", spacing="4dp")
        kat_box.add_widget(self.input_kategori)
        kat_box.add_widget(btn_drop)

        content = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="130dp")
        content.add_widget(self.input_judul)
        content.add_widget(kat_box)

        self.dialog = MDDialog(
            title=f"Tambah {self.current_filter}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="BATAL", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(
                    text="SIMPAN",
                    md_bg_color=(0.12, 0.53, 0.90, 1),
                    on_release=lambda x: self.save_task()
                )
            ]
        )
        self.dialog.open()

    def open_category_menu(self, instance):
        categories = ["Sekolah", "Kuliah", "Pekerjaan", "Pribadi", "Kesehatan", "Lainnya"]
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": cat,
                "on_release": lambda x=cat: self.set_category(x),
            } for cat in categories
        ]
        self.category_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.category_menu.open()

    def set_category(self, text_item):
        self.input_kategori.text = text_item
        if self.category_menu:
            self.category_menu.dismiss()

    def save_task(self):
        judul = self.input_judul.text.strip()
        kategori = self.input_kategori.text.strip()
        if not kategori:
            kategori = "Umum"

        if judul:
            app = MDApp.get_running_app()
            database.add_task(app.current_user_id, judul, kategori, self.current_filter)
            self.dialog.dismiss()
            self.load_tasks()

    def open_edit_profile(self):
        self.manager.get_screen("edit_profile").setup_data()
        self.manager.current = "edit_profile"

    def do_logout(self):
        app = MDApp.get_running_app()
        app.current_user_id = None
        app.current_user_nama = ""
        app.current_user_email = ""
        app.current_user_password = ""
        app.current_user_avatar = "account"
        self.manager.current = "login"


class EditProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_avatar = "account"

    def setup_data(self):
        app = MDApp.get_running_app()
        self.ids.edit_nama_input.text = app.current_user_nama
        self.ids.edit_email_input.text = app.current_user_email
        self.selected_avatar = app.current_user_avatar if app.current_user_avatar else "account"
        self.ids.avatar_preview_icon.icon = self.selected_avatar

        self.ids.pass_old.text = ""
        self.ids.pass_new.text = ""
        self.ids.pass_confirm.text = ""

    def select_avatar(self, icon_name):
        self.selected_avatar = icon_name
        self.ids.avatar_preview_icon.icon = icon_name

    def save_changes(self):
        app = MDApp.get_running_app()
        nama = self.ids.edit_nama_input.text.strip()
        email = self.ids.edit_email_input.text.strip()

        pass_old = self.ids.pass_old.text.strip()
        pass_new = self.ids.pass_new.text.strip()
        pass_confirm = self.ids.pass_confirm.text.strip()

        if not nama or not email:
            self.show_dialog("Peringatan", "Nama dan Email tidak boleh kosong!")
            return

        if pass_old or pass_new or pass_confirm:
            if pass_old != app.current_user_password:
                self.show_dialog("Gagal", "Kata sandi lama tidak cocok!")
                return
            if len(pass_new) < 4:
                self.show_dialog("Peringatan", "Kata sandi baru minimal 4 karakter!")
                return
            if pass_new != pass_confirm:
                self.show_dialog("Gagal", "Konfirmasi kata sandi baru tidak sesuai!")
                return

            database.update_user_password(app.current_user_id, pass_new)
            app.current_user_password = pass_new

        success = database.update_user_profile(app.current_user_id, nama, email, self.selected_avatar)
        if success:
            app.current_user_nama = nama
            app.current_user_email = email
            app.current_user_avatar = self.selected_avatar

            self.manager.get_screen("main").setup_user_data()
            self.show_dialog("Berhasil", "Profil berhasil diperbarui!", callback=self.go_back)
        else:
            self.show_dialog("Gagal", "Email sudah digunakan pengguna lain!")

    def go_back(self):
        self.manager.current = "main"

    def show_dialog(self, title, text, callback=None):
        def on_dismiss(x):
            dialog.dismiss()
            if callback:
                callback()

        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=on_dismiss,
                    theme_text_color="Custom",
                    text_color=(0.12, 0.53, 0.90, 1)
                )
            ]
        )
        dialog.open()


class DoItApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.current_user_id = None
        self.current_user_nama = ""
        self.current_user_email = ""
        self.current_user_password = ""
        self.current_user_avatar = "account"

        database.init_db()
        return Builder.load_file("doit.kv")


if __name__ == "__main__":
    DoItApp().run()