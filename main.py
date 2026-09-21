import database
from datetime import datetime, timedelta

from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')

from kivy.core.window import Window
Window.size = (360, 640)

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconRightWidget
from kivymd.uix.pickers import MDDatePicker


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
                app.current_user_avatar = user[4] if len(user) > 4 and user[4] else "avatars/avatar1.png"

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
        self.selected_deadline = None

    def setup_user_data(self):
        app = MDApp.get_running_app()
        
        hour = datetime.now().hour
        if 0 <= hour < 11:
            salam = "Selamat Pagi"
        elif 11 <= hour < 15:
            salam = "Selamat Siang"
        elif 15 <= hour < 19:
            salam = "Selamat Sore"
        else:
            salam = "Selamat Malam"

        self.ids.greeting_label.text = f"{salam}, {app.current_user_nama}!"
        self.ids.profile_nama.text = app.current_user_nama
        self.ids.profile_email.text = app.current_user_email
        self.ids.profile_avatar_img.source = app.current_user_avatar if app.current_user_avatar else "avatars/avatar1.png"
        self.ids.date_label.text = datetime.now().strftime("%d %b %Y")

        self.switch_tab("tab_beranda")
        self.load_tasks()
        self.load_history()
        self.update_streak()
        self.load_weekly_chart()
        self.load_user_stats()

    def switch_tab(self, tab_name):
        self.ids.main_sm.current = tab_name
        gray = (0.5, 0.5, 0.5, 1)
        blue = (0.12, 0.53, 0.90, 1)

        self.ids.nav_home.icon_color = gray
        self.ids.nav_stats.icon_color = gray
        self.ids.nav_profile.icon_color = gray

        if tab_name == "tab_beranda":
            self.ids.nav_home.icon_color = blue
        elif tab_name == "tab_statistik":
            self.ids.nav_stats.icon_color = blue
        elif tab_name == "tab_profil":
            self.ids.nav_profile.icon_color = blue

    def load_user_stats(self):
        app = MDApp.get_running_app()
        total, completed = database.get_user_stats(app.current_user_id)
        
        if total > 0:
            percentage = int((completed / total) * 100)
        else:
            percentage = 0

        self.ids.stat_progress_bar.value = percentage
        self.ids.stat_percent_label.text = f"{percentage}%"
        self.ids.stat_summary_label.text = f"{completed} dari {total} tugas selesai"

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

        today = datetime.now().date()

        for task in tasks:
            try:
                t_id = task[0]
                judul = task[2]
                kategori = task[3]
                deadline_str = task[7] if len(task) > 7 else None

                card = MDCard(
                    size_hint=(1, None),
                    height="68dp" if deadline_str else "60dp",
                    elevation=1,
                    radius=[12],
                    padding=["10dp", "4dp", "10dp", "4dp"],
                    md_bg_color=app.theme_cls.bg_light
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
                
                sub_info = f"Kategori: {kategori}"
                text_box.add_widget(MDLabel(text=sub_info, font_style="Caption", theme_text_color="Secondary"))

                if deadline_str:
                    try:
                        d_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                        if d_date < today:
                            d_color = (0.85, 0.1, 0.1, 1)
                            txt_dl = f"Deadline: {deadline_str} (Terlewat)"
                        elif d_date == today:
                            d_color = (0.9, 0.5, 0.0, 1)
                            txt_dl = f"Deadline: Hari Ini"
                        else:
                            d_color = (0.12, 0.53, 0.90, 1)
                            txt_dl = f"Deadline: {deadline_str}"

                        lbl_dl = MDLabel(text=txt_dl, font_style="Caption", bold=True, theme_text_color="Custom", text_color=d_color)
                        text_box.add_widget(lbl_dl)
                    except Exception:
                        pass

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
        self.load_user_stats()

    def delete_task(self, task_id):
        database.delete_task(task_id)
        self.load_tasks()
        self.load_user_stats()

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
                    md_bg_color=app.theme_cls.bg_light
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
                text_box.add_widget(MDLabel(text=f"Selesai: {tgl}", font_style="Caption", theme_text_color="Secondary"))

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

    def open_all_history_dialog(self):
        app = MDApp.get_running_app()
        all_history = database.get_all_completed_tasks_by_user(app.current_user_id)

        scroll = ScrollView(size_hint_y=None, height="260dp")
        list_box = MDBoxLayout(orientation="vertical", spacing="8dp", size_hint_y=None)
        list_box.bind(minimum_height=list_box.setter('height'))

        if not all_history:
            list_box.add_widget(MDLabel(
                text="Belum ada riwayat tugas yang selesai.",
                halign="center",
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_y=None,
                height="40dp"
            ))
        else:
            for h in all_history:
                judul = h[1]
                tgl = h[3] if len(h) >= 4 else "-"
                
                card = MDCard(
                    size_hint=(1, None),
                    height="52dp",
                    elevation=0,
                    radius=[8],
                    padding=["10dp", "4dp", "10dp", "4dp"],
                    md_bg_color=app.theme_cls.bg_light
                )
                box = MDBoxLayout(orientation="horizontal", spacing="10dp", pos_hint={"center_y": 0.5})
                
                icon = MDIconButton(
                    icon="check-circle",
                    theme_icon_color="Custom",
                    icon_color=(0.12, 0.7, 0.3, 1),
                    pos_hint={"center_y": 0.5}
                )
                
                txt_box = MDBoxLayout(orientation="vertical", pos_hint={"center_y": 0.5})
                txt_box.add_widget(MDLabel(text=str(judul), bold=True, font_style="Body2", theme_text_color="Primary"))
                txt_box.add_widget(MDLabel(text=f"Selesai pada: {tgl}", font_style="Caption", theme_text_color="Secondary"))
                
                box.add_widget(icon)
                box.add_widget(txt_box)
                card.add_widget(box)
                list_box.add_widget(card)

        scroll.add_widget(list_box)

        dlg = MDDialog(
            title="Seluruh Riwayat Selesai",
            type="custom",
            content_cls=scroll,
            buttons=[
                MDFlatButton(
                    text="TUTUP",
                    theme_text_color="Custom",
                    text_color=(0.12, 0.53, 0.90, 1),
                    on_release=lambda x: dlg.dismiss()
                )
            ]
        )
        dlg.open()

    def delete_history(self, task_id):
        database.delete_task(task_id)
        self.load_history()
        self.update_streak()
        self.load_weekly_chart()
        self.load_user_stats()

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
        app = MDApp.get_running_app()
        user_cats = database.get_user_categories(app.current_user_id)
        first_cat = user_cats[0][1] if user_cats else "Umum"
        self.selected_deadline = None

        self.input_judul = MDTextField(hint_text="Nama Tugas / Kebiasaan")
        self.input_kategori = MDTextField(
            hint_text="Pilih Kategori",
            text=first_cat,
            readonly=True
        )
        
        btn_drop = MDIconButton(
            icon="menu-down",
            pos_hint={"center_y": 0.5}
        )
        btn_drop.bind(on_release=self.open_category_menu)

        btn_manage_cat = MDIconButton(
            icon="plus-circle-outline",
            theme_icon_color="Custom",
            icon_color=(0.12, 0.53, 0.90, 1),
            pos_hint={"center_y": 0.5}
        )
        btn_manage_cat.bind(on_release=lambda x: self.open_manage_categories_dialog())

        kat_box = MDBoxLayout(orientation="horizontal", spacing="4dp")
        kat_box.add_widget(self.input_kategori)
        kat_box.add_widget(btn_drop)
        kat_box.add_widget(btn_manage_cat)

        self.input_deadline = MDTextField(
            hint_text="Batas Waktu (Opsional)",
            readonly=True
        )
        btn_picker = MDIconButton(
            icon="calendar",
            pos_hint={"center_y": 0.5},
            on_release=self.open_date_picker
        )

        dl_box = MDBoxLayout(orientation="horizontal", spacing="4dp")
        dl_box.add_widget(self.input_deadline)
        dl_box.add_widget(btn_picker)

        content = MDBoxLayout(orientation="vertical", spacing="10dp", size_hint_y=None, height="180dp")
        content.add_widget(self.input_judul)
        content.add_widget(kat_box)
        content.add_widget(dl_box)

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

    def open_date_picker(self, instance):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self.selected_deadline = value.strftime("%Y-%m-%d")
        self.input_deadline.text = self.selected_deadline

    def open_category_menu(self, instance):
        app = MDApp.get_running_app()
        user_cats = database.get_user_categories(app.current_user_id)
        
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": cat[1],
                "on_release": lambda x=cat[1]: self.set_category(x),
            } for cat in user_cats
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
            database.add_task(app.current_user_id, judul, kategori, self.current_filter, self.selected_deadline)
            self.dialog.dismiss()
            self.load_tasks()
            self.load_user_stats()

    def open_manage_categories_dialog(self):
        self.input_new_cat = MDTextField(hint_text="Kategori Baru", size_hint_x=0.7)
        btn_add = MDRaisedButton(
            text="Tambah",
            size_hint_x=0.3,
            md_bg_color=(0.12, 0.53, 0.90, 1),
            on_release=lambda x: self.add_new_category()
        )

        add_box = MDBoxLayout(orientation="horizontal", spacing="8dp", size_hint_y=None, height="48dp")
        add_box.add_widget(self.input_new_cat)
        add_box.add_widget(btn_add)

        self.cat_list_box = MDList(spacing="4dp")
        
        scroll = ScrollView(size_hint_y=None, height="180dp")
        scroll.add_widget(self.cat_list_box)

        self.refresh_category_list_items()

        content = MDBoxLayout(orientation="vertical", spacing="10dp", size_hint_y=None, height="240dp")
        content.add_widget(add_box)
        content.add_widget(scroll)

        self.cat_dialog = MDDialog(
            title="Kelola Kategori",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="TUTUP", on_release=lambda x: self.cat_dialog.dismiss())
            ]
        )
        self.cat_dialog.open()

    def refresh_category_list_items(self):
        self.cat_list_box.clear_widgets()
        app = MDApp.get_running_app()
        user_cats = database.get_user_categories(app.current_user_id)

        for c_id, c_name in user_cats:
            item = OneLineAvatarIconListItem(text=c_name)
            del_icon = IconRightWidget(icon="trash-can-outline")
            del_icon.bind(on_release=lambda x, cid=c_id: self.delete_category_item(cid))
            item.add_widget(del_icon)
            self.cat_list_box.add_widget(item)

    def add_new_category(self):
        cat_name = self.input_new_cat.text.strip()
        if cat_name:
            app = MDApp.get_running_app()
            database.add_category(app.current_user_id, cat_name)
            self.input_new_cat.text = ""
            self.refresh_category_list_items()

    def delete_category_item(self, cat_id):
        database.delete_category(cat_id)
        self.refresh_category_list_items()

    def open_edit_profile(self):
        self.manager.get_screen("edit_profile").setup_data()
        self.manager.current = "edit_profile"

    # PERBAIKAN: Perubahan tema dinamis tanpa merusak susunan antarmuka
    def toggle_theme(self, switch_active):
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark" if switch_active else "Light"
        self.load_tasks()
        self.load_history()

    def do_logout(self):
        app = MDApp.get_running_app()
        app.current_user_id = None
        app.current_user_nama = ""
        app.current_user_email = ""
        app.current_user_password = ""
        app.current_user_avatar = "avatars/avatar1.png"
        self.manager.current = "login"


class EditProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_avatar = "avatars/avatar1.png"

    def setup_data(self):
        app = MDApp.get_running_app()
        self.ids.edit_nama_input.text = app.current_user_nama
        self.ids.edit_email_input.text = app.current_user_email
        self.selected_avatar = app.current_user_avatar if app.current_user_avatar else "avatars/avatar1.png"
        self.ids.avatar_preview_img.source = self.selected_avatar

        self.ids.pass_old.text = ""
        self.ids.pass_new.text = ""
        self.ids.pass_confirm.text = ""

    def select_avatar(self, avatar_path):
        self.selected_avatar = avatar_path
        self.ids.avatar_preview_img.source = avatar_path

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
        self.current_user_avatar = "avatars/avatar1.png"

        database.init_db()
        return Builder.load_file("doit.kv")


if __name__ == "__main__":
    DoItApp().run()