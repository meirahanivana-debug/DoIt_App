import database
from datetime import datetime, timedelta

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')

from kivy.core.window import Window
Window.size = (360, 640)

from kivy.lang import Builder
from kivy.clock import Clock
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
from kivymd.uix.pickers import MDDatePicker, MDTimePicker


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
                database.save_session(user[2])
                app = MDApp.get_running_app()
                app.current_user_id = user[0]
                app.current_user_nama = user[1]
                app.current_user_email = user[2]
                app.current_user_password = user[3]
                app.current_user_avatar = user[4] if len(user) > 4 and user[4] else "avatars/avatar1.png"
                app.current_user_created_at = user[5] if len(user) > 5 and user[5] else "-"

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

        if not email.endswith("@gmail.com"):
            self.show_dialog("Pendaftaran Gagal", "Harap gunakan akun email dengan domain @gmail.com yang valid.")
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
        self.sort_by = "default"
        self.search_query = ""
        self.chart_mode = "weekly"
        self.dialog = None
        self.logout_dialog = None
        self.category_menu = None
        self.sort_menu = None
        self.selected_date = None
        self.selected_time = None
        self.editing_task_id = None

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
        
        created_at_val = app.current_user_created_at
        if created_at_val and created_at_val != "-":
            try:
                dt_created = datetime.strptime(created_at_val, "%Y-%m-%d")
                created_at_val = dt_created.strftime("%d-%m-%Y")
            except Exception:
                pass
        self.ids.profile_created_at.text = f"Bergabung: {created_at_val}"
        
        self.ids.date_label.text = datetime.now().strftime("%d %b %Y")

        self.apply_header_color()
        self.switch_tab("tab_beranda")
        self.load_tasks()
        self.load_history()
        self.update_streak()
        self.load_chart_data()
        self.load_user_stats()

    def apply_header_color(self):
        header_color = (0.12, 0.53, 0.90, 1)
        self.ids.main_header.md_bg_color = header_color
        
        edit_screen = self.manager.get_screen("edit_profile") if self.manager else None
        if edit_screen and "edit_profile_header" in edit_screen.ids:
            edit_screen.ids.edit_profile_header.md_bg_color = header_color

    def switch_tab(self, tab_name):
        self.ids.main_sm.current = tab_name
        gray = (0.5, 0.5, 0.5, 1)
        blue = (0.12, 0.53, 0.90, 1)

        self.ids.nav_home.icon_color = gray
        self.ids.nav_stats.icon_color = gray
        self.ids.nav_profile.icon_color = gray

        if tab_name == "tab_beranda":
            self.ids.nav_home.icon_color = blue
            self.ids.main_header.height = "128dp"
            self.ids.main_header.opacity = 1
        elif tab_name == "tab_statistik":
            self.ids.nav_stats.icon_color = blue
            self.ids.main_header.height = "128dp"
            self.ids.main_header.opacity = 1
        elif tab_name == "tab_profil":
            self.ids.nav_profile.icon_color = blue
            self.ids.main_header.height = "0dp"
            self.ids.main_header.opacity = 0

    def load_user_stats(self):
        pass

    def switch_filter(self, filter_type):
        self.current_filter = filter_type
        if filter_type == "Tugas":
            self.ids.btn_tugas.md_bg_color = (0.12, 0.53, 0.90, 1)
            self.ids.btn_tugas.text_color = (1, 1, 1, 1)
            self.ids.btn_tugas.elevation = 1
            self.ids.btn_kebiasaan.md_bg_color = (0.85, 0.88, 0.92, 1)
            self.ids.btn_kebiasaan.text_color = (0.3, 0.3, 0.3, 1)
            self.ids.btn_kebiasaan.elevation = 0
        else:
            self.ids.btn_kebiasaan.md_bg_color = (0.12, 0.53, 0.90, 1)
            self.ids.btn_kebiasaan.text_color = (1, 1, 1, 1)
            self.ids.btn_kebiasaan.elevation = 1
            self.ids.btn_tugas.md_bg_color = (0.85, 0.88, 0.92, 1)
            self.ids.btn_tugas.text_color = (0.3, 0.3, 0.3, 1)
            self.ids.btn_tugas.elevation = 0
        self.load_tasks()

    def set_chart_mode(self, mode):
        self.chart_mode = mode
        if mode == "weekly":
            self.ids.btn_chart_weekly.md_bg_color = (0.12, 0.53, 0.90, 1)
            self.ids.btn_chart_weekly.text_color = (1, 1, 1, 1)
            self.ids.btn_chart_weekly.elevation = 1
            self.ids.btn_chart_monthly.md_bg_color = (0.85, 0.88, 0.92, 1)
            self.ids.btn_chart_monthly.text_color = (0.3, 0.3, 0.3, 1)
            self.ids.btn_chart_monthly.elevation = 0
            self.ids.chart_title_label.text = "Tugas Selesai (Kalender Mingguan)"
        else:
            self.ids.btn_chart_monthly.md_bg_color = (0.12, 0.53, 0.90, 1)
            self.ids.btn_chart_monthly.text_color = (1, 1, 1, 1)
            self.ids.btn_chart_monthly.elevation = 1
            self.ids.btn_chart_weekly.md_bg_color = (0.85, 0.88, 0.92, 1)
            self.ids.btn_chart_weekly.text_color = (0.3, 0.3, 0.3, 1)
            self.ids.btn_chart_weekly.elevation = 0
            self.ids.chart_title_label.text = "Tugas Selesai (4 Minggu Terakhir)"
        self.load_chart_data()

    def on_search_text_change(self, text):
        self.search_query = text.strip()
        self.load_tasks()

    def open_sort_menu(self, instance):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Terbaru (Default)",
                "on_release": lambda x="default": self.set_sort_option(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Deadline Terdekat",
                "on_release": lambda x="deadline": self.set_sort_option(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Abjad (A-Z)",
                "on_release": lambda x="alphabet": self.set_sort_option(x),
            },
        ]
        self.sort_menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.sort_menu.open()

    def set_sort_option(self, option):
        self.sort_by = option
        if self.sort_menu:
            self.sort_menu.dismiss()
        self.load_tasks()

    def load_tasks(self):
        self.ids.task_list.clear_widgets()
        app = MDApp.get_running_app()
        tasks = database.get_tasks_by_user(app.current_user_id, self.current_filter, self.sort_by, self.search_query)

        if not tasks:
            empty_box = MDBoxLayout(orientation="vertical", spacing="6dp", size_hint_y=None, height="140dp", pos_hint={"center_x": 0.5})
            icon_empty = MDIconButton(
                icon="playlist-remove",
                theme_icon_color="Custom",
                icon_color=(0.6, 0.6, 0.6, 1),
                pos_hint={"center_x": 0.5}
            )
            lbl_empty = MDLabel(
                text="Belum ada aktivitas tercatat",
                halign="center",
                font_style="Body2",
                theme_text_color="Secondary"
            )
            empty_box.add_widget(icon_empty)
            empty_box.add_widget(lbl_empty)
            self.ids.task_list.add_widget(empty_box)
            return

        now = datetime.now()

        for task in tasks:
            try:
                t_id = task[0]
                judul = task[2]
                kategori = task[3]
                deadline_str = task[7] if len(task) > 7 else None

                card = MDCard(
                    size_hint=(1, None),
                    height="78dp" if deadline_str else "70dp",
                    elevation=0.5,
                    shadow_color=(0, 0, 0, 0.05),
                    radius=[12, 12, 12, 12],
                    padding=["12dp", "6dp", "12dp", "6dp"],
                    md_bg_color=app.theme_cls.bg_light
                )

                layout = MDBoxLayout(orientation="horizontal", spacing="10dp", pos_hint={"center_y": 0.5})

                chk_btn = MDIconButton(
                    icon="checkbox-blank-outline",
                    theme_icon_color="Custom",
                    icon_color=(0.5, 0.5, 0.5, 1),
                    pos_hint={"center_y": 0.5}
                )
                chk_btn.bind(on_release=lambda btn, tid=t_id: self.mark_done_with_anim(btn, tid))

                text_box = MDBoxLayout(orientation="vertical", spacing="4dp", pos_hint={"center_y": 0.5})
                text_box.add_widget(MDLabel(text=str(judul), bold=True, font_style="Subtitle2", theme_text_color="Primary"))
                
                sub_info = f"Kategori: {kategori}"
                text_box.add_widget(MDLabel(text=sub_info, font_style="Caption", theme_text_color="Secondary"))

                if deadline_str:
                    try:
                        if len(deadline_str) > 10:
                            d_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
                        else:
                            d_dt = datetime.strptime(deadline_str, "%Y-%m-%d").replace(hour=23, minute=59)

                        dl_display_time = d_dt.strftime('%H:%M')
                        dl_display_date = d_dt.strftime('%d-%m-%Y')

                        if d_dt < now:
                            d_color = (0.85, 0.1, 0.1, 1)
                            txt_dl = f"Deadline: {dl_display_date} {dl_display_time} (Terlewat)"
                        elif d_dt.date() == now.date():
                            d_color = (0.9, 0.5, 0.0, 1)
                            txt_dl = f"Deadline: Hari Ini ({dl_display_time})"
                        else:
                            d_color = (0.12, 0.53, 0.90, 1)
                            txt_dl = f"Deadline: {dl_display_date} {dl_display_time}"

                        lbl_dl = MDLabel(text=txt_dl, font_style="Caption", bold=True, theme_text_color="Custom", text_color=d_color)
                        text_box.add_widget(lbl_dl)
                    except Exception:
                        pass

                edit_btn = MDIconButton(
                    icon="pencil-outline",
                    theme_icon_color="Custom",
                    icon_color=(0.12, 0.53, 0.90, 1),
                    pos_hint={"center_y": 0.5}
                )
                edit_btn.bind(on_release=lambda x, t_data=task: self.open_edit_task_dialog(t_data))

                del_btn = MDIconButton(
                    icon="trash-can-outline",
                    theme_icon_color="Custom",
                    icon_color=(0.9, 0.2, 0.2, 1),
                    pos_hint={"center_y": 0.5}
                )
                del_btn.bind(on_release=lambda x, tid=t_id: self.delete_task(tid))

                layout.add_widget(chk_btn)
                layout.add_widget(text_box)
                layout.add_widget(edit_btn)
                layout.add_widget(del_btn)

                card.add_widget(layout)
                self.ids.task_list.add_widget(card)
            except Exception:
                continue

    def mark_done_with_anim(self, icon_button, task_id):
        icon_button.disabled = True
        icon_button.icon = "check-circle"
        icon_button.icon_color = (0.2, 0.7, 0.3, 1)

        Clock.schedule_once(lambda dt: self.execute_mark_done(task_id), 0.3)

    def execute_mark_done(self, task_id):
        database.update_task_status(task_id, "Selesai")
        self.load_tasks()
        self.load_history()
        self.update_streak()
        self.load_chart_data()
        self.load_user_stats()

    def delete_task(self, task_id):
        database.delete_task(task_id)
        self.load_tasks()
        self.load_user_stats()

    def load_history(self):
        self.ids.history_list.clear_widgets()
        app = MDApp.get_running_app()
        history = database.get_completed_tasks_by_user(app.current_user_id)

        if not history:
            empty_box = MDBoxLayout(orientation="vertical", spacing="4dp", size_hint_y=None, height="100dp", pos_hint={"center_x": 0.5})
            icon_empty = MDIconButton(
                icon="chart-timeline-variant-off",
                theme_icon_color="Custom",
                icon_color=(0.6, 0.6, 0.6, 1),
                pos_hint={"center_x": 0.5}
            )
            lbl_empty = MDLabel(
                text="Belum ada riwayat aktivitas",
                halign="center",
                font_style="Caption",
                theme_text_color="Secondary"
            )
            empty_box.add_widget(icon_empty)
            empty_box.add_widget(lbl_empty)
            self.ids.history_list.add_widget(empty_box)
            return

        for h in history:
            try:
                t_id = h[0]
                judul = h[1]
                tgl = h[3] if len(h) >= 4 else "-"

                if tgl and tgl != "-":
                    try:
                        tgl_dt = datetime.strptime(tgl, "%Y-%m-%d")
                        tgl = tgl_dt.strftime("%d-%m-%Y")
                    except Exception:
                        pass

                card = MDCard(
                    size_hint=(1, None),
                    height="56dp",
                    elevation=0.5,
                    shadow_color=(0, 0, 0, 0.05),
                    radius=[10, 10, 10, 10],
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
                
                if tgl and tgl != "-":
                    try:
                        tgl_dt = datetime.strptime(tgl, "%Y-%m-%d")
                        tgl = tgl_dt.strftime("%d-%m-%Y")
                    except Exception:
                        pass
                
                card = MDCard(
                    size_hint=(1, None),
                    height="52dp",
                    elevation=0,
                    radius=[8, 8, 8, 8],
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
        self.load_chart_data()
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

    def load_chart_data(self):
        self.ids.chart_container.clear_widgets()
        app = MDApp.get_running_app()
        
        if self.chart_mode == "weekly":
            chart_data = database.get_weekly_completed_counts(app.current_user_id)
        else:
            chart_data = database.get_monthly_completed_counts(app.current_user_id)

        total_activity = sum(cnt for _, cnt in chart_data)

        if total_activity == 0:
            empty_box = MDBoxLayout(
                orientation="vertical",
                spacing="4dp",
                size_hint=(1, 1),
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )
            lbl_empty = MDLabel(
                text="Belum ada aktivitas tercatat pada periode ini",
                halign="center",
                font_style="Caption",
                theme_text_color="Secondary"
            )
            empty_box.add_widget(lbl_empty)
            self.ids.chart_container.add_widget(empty_box)
            return

        for label_text, cnt in chart_data:
            col = MDBoxLayout(orientation="vertical", spacing="4dp")

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

            desc_label = MDLabel(text=label_text, font_style="Caption", halign="center", bold=True, theme_text_color="Primary", size_hint_y=None, height="14dp")

            col.add_widget(val_label)
            col.add_widget(bar_card)
            col.add_widget(desc_label)

            self.ids.chart_container.add_widget(col)

    def show_add_task_dialog(self):
        self.editing_task_id = None
        self._build_task_dialog(title=f"Tambah {self.current_filter}")

    def open_edit_task_dialog(self, task_data):
        self.editing_task_id = task_data[0]
        judul = task_data[2]
        kategori = task_data[3]
        deadline_str = task_data[7] if len(task_data) > 7 else None

        d_str = ""
        t_str = ""
        if deadline_str:
            parts = deadline_str.split(" ")
            d_str = parts[0]
            if len(parts) > 1:
                t_str = parts[1]

        self._build_task_dialog(
            title=f"Edit {self.current_filter}",
            init_judul=judul,
            init_kategori=kategori,
            init_date=d_str,
            init_time=t_str
        )

    def _build_task_dialog(self, title, init_judul="", init_kategori="", init_date="", init_time=""):
        app = MDApp.get_running_app()
        user_cats = database.get_user_categories(app.current_user_id)
        default_cat = init_kategori if init_kategori else (user_cats[0][1] if user_cats else "Umum")
        
        self.selected_date = init_date if init_date else None
        self.selected_time = init_time if init_time else None

        self.input_judul = MDTextField(hint_text="Nama Tugas / Kebiasaan", text=init_judul)
        self.input_kategori = MDTextField(
            hint_text="Pilih Kategori",
            text=default_cat,
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

        self.input_date = MDTextField(
            hint_text="Tanggal Deadline",
            text=init_date,
            readonly=True
        )
        btn_date_picker = MDIconButton(
            icon="calendar",
            pos_hint={"center_y": 0.5},
            on_release=self.open_date_picker
        )
        date_box = MDBoxLayout(orientation="horizontal", spacing="4dp")
        date_box.add_widget(self.input_date)
        date_box.add_widget(btn_date_picker)

        self.input_time = MDTextField(
            hint_text="Jam Deadline (Opsional)",
            text=init_time,
            readonly=True
        )
        btn_time_picker = MDIconButton(
            icon="clock-outline",
            pos_hint={"center_y": 0.5},
            on_release=self.open_time_picker
        )
        time_box = MDBoxLayout(orientation="horizontal", spacing="4dp")
        time_box.add_widget(self.input_time)
        time_box.add_widget(btn_time_picker)

        content = MDBoxLayout(orientation="vertical", spacing="10dp", size_hint_y=None, height="240dp")
        content.add_widget(self.input_judul)
        content.add_widget(kat_box)
        content.add_widget(date_box)
        content.add_widget(time_box)

        self.dialog = MDDialog(
            title=title,
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
        self.selected_date = value.strftime("%Y-%m-%d")
        self.input_date.text = self.selected_date

    def open_time_picker(self, instance):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_time_save)
        time_dialog.open()

    def on_time_save(self, instance, time_obj):
        try:
            if hasattr(time_obj, 'hour') and hasattr(time_obj, 'minute'):
                formatted_time = f"{time_obj.hour:02d}:{time_obj.minute:02d}"
            elif hasattr(time_obj, 'strftime'):
                formatted_time = time_obj.strftime("%H:%M")
            else:
                formatted_time = str(time_obj)[:5]
        except Exception:
            formatted_time = str(time_obj)

        self.selected_time = formatted_time
        self.input_time.text = self.selected_time

    def open_category_menu(self, instance):
        app = MDApp.get_running_app()
        user_cats = database.get_user_categories(app.current_user_id)
        
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": cat[1],
                "theme_text_color": "Primary",
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

    def trigger_task_notification(self, judul, deadline_str):
        if not PLYER_AVAILABLE:
            return
        
        try:
            notif_title = "Pengingat Tugas DoIt!"
            notif_text = f"Tugas baru: '{judul}' berhasil dijadwalkan."
            if deadline_str:
                notif_text += f" Tenggat: {deadline_str}"

            notification.notify(
                title=notif_title,
                message=notif_text,
                app_name="DoIt",
                app_icon=""
            )
        except Exception as e:
            print(f"Gagal memicu notifikasi: {e}")

    def save_task(self):
        judul = self.input_judul.text.strip()
        kategori = self.input_kategori.text.strip()
        
        date_part = self.input_date.text.strip()
        time_part = self.input_time.text.strip()

        if time_part and not date_part:
            date_part = datetime.now().strftime("%Y-%m-%d")

        if date_part and time_part:
            deadline = f"{date_part} {time_part}"
        elif date_part:
            deadline = date_part
        else:
            deadline = None

        if not kategori:
            kategori = "Umum"

        if judul:
            app = MDApp.get_running_app()
            if self.editing_task_id:
                database.update_task(self.editing_task_id, judul, kategori, deadline)
            else:
                database.add_task(app.current_user_id, app.current_user_email, judul, kategori, self.current_filter, deadline)
            
            self.trigger_task_notification(judul, deadline)

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

    def open_logout_confirmation(self):
        self.logout_dialog = MDDialog(
            title="Konfirmasi Keluar",
            text="Apakah Anda yakin ingin keluar dari akun ini?",
            buttons=[
                MDFlatButton(
                    text="Batal",
                    theme_text_color="Custom",
                    text_color=(0.3, 0.3, 0.3, 1),
                    on_release=lambda x: self.logout_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Ya, Keluar",
                    md_bg_color=(0.88, 0.2, 0.2, 1),
                    on_release=lambda x: self.execute_logout()
                )
            ]
        )
        self.logout_dialog.open()

    def execute_logout(self):
        if self.logout_dialog:
            self.logout_dialog.dismiss()
        database.clear_session()
        app = MDApp.get_running_app()
        app.current_user_id = None
        app.current_user_nama = ""
        app.current_user_email = ""
        app.current_user_password = ""
        app.current_user_avatar = "avatars/avatar1.png"
        app.current_user_created_at = "-"
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
            database.save_session(email)
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
        self.theme_cls.theme_style = "Light"
        self.current_user_id = None
        self.current_user_nama = ""
        self.current_user_email = ""
        self.current_user_password = ""
        self.current_user_avatar = "avatars/avatar1.png"
        self.current_user_created_at = "-"

        database.init_db()

        active_email = database.get_active_session()
        if active_email:
            user = database.get_user_by_email(active_email)
            if user:
                self.current_user_id = user[0]
                self.current_user_nama = user[1]
                self.current_user_email = user[2]
                self.current_user_password = user[3]
                self.current_user_avatar = user[4] if len(user) > 4 and user[4] else "avatars/avatar1.png"
                self.current_user_created_at = user[5] if len(user) > 5 and user[5] else "-"
                
                Clock.schedule_numbers_once = lambda *args: None
                Clock.schedule_once(lambda dt: self.to_main_screen(), 0.1)

        return Builder.load_file("doit.kv")

    def to_main_screen(self):
        if self.root:
            main_scr = self.root.get_screen("main")
            main_scr.setup_user_data()
            self.root.current = "main"

    def open_help_dialog(self):
        help_content = MDBoxLayout(
            orientation="vertical",
            spacing="10dp",
            size_hint_y=None,
            height="220dp"
        )
        
        scroll = ScrollView(size_hint=(1, 1))
        inner_box = MDBoxLayout(orientation="vertical", spacing="8dp", size_hint_y=None)
        inner_box.bind(minimum_height=inner_box.setter('height'))
        
        faq_text = (
            "[b]1. Bagaimana cara menambah tugas?[/b]\n"
            "Tekan tombol ikon plus (+) mengambang di pojok kanan bawah halaman utama.\n\n"
            "[b]2. Bagaimana melihat statistik?[/b]\n"
            "Pilih ikon grafik batang pada menu navigasi bawah untuk melihat streak dan grafik tugas selesai.\n\n"
            "[b]3. Bagaimana cara mengubah profil?[/b]\n"
            "Masuk ke tab Profil, lalu ketuk tombol 'Edit Profil'."
        )
        
        lbl = MDLabel(
            text=faq_text,
            markup=True,
            font_style="Body2",
            theme_text_color="Primary",
            size_hint_y=None
        )
        lbl.bind(texture_size=lambda *x: setattr(lbl, 'height', lbl.texture_size[1]))
        
        inner_box.add_widget(lbl)
        scroll.add_widget(inner_box)
        help_content.add_widget(scroll)

        self.help_dialog = MDDialog(
            title="Pusat Bantuan & Panduan",
            type="custom",
            content_cls=help_content,
            buttons=[
                MDFlatButton(
                    text="TUTUP",
                    theme_text_color="Custom",
                    text_color=(0.12, 0.53, 0.90, 1),
                    on_release=lambda x: self.help_dialog.dismiss()
                )
            ]
        )
        self.help_dialog.open()


if __name__ == "__main__":
    DoItApp().run()