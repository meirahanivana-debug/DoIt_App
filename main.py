from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton, MDFabButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogContentContainer, MDDialogButtonContainer
from kivy.lang import Builder
from kivy.core.window import Window
import sqlite3
from datetime import date, datetime, timedelta

Window.size = (360, 640)

KV = '''
<LoginScreen>:
    name: 'login'
    MDFloatLayout:
        md_bg_color: 0.12, 0.53, 0.90, 1
        
        MDLabel:
            text: "DoIt!"
            font_style: "Headline"
            role: "large"
            bold: True
            halign: "center"
            pos_hint: {"center_y": 0.85}
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1

        MDCard:
            size_hint: 0.88, 0.52
            pos_hint: {"center_x": 0.5, "center_y": 0.42}
            elevation: 2
            radius: [20]
            padding: 20
            spacing: 12
            orientation: "vertical"
            md_bg_color: 1, 1, 1, 1

            MDLabel:
                text: "Masuk ke Akun"
                font_style: "Title"
                role: "medium"
                bold: True

            MDTextField:
                id: email_input
                mode: "outlined"
                MDTextFieldHintText:
                    text: "Email"

            MDTextField:
                id: pass_input
                mode: "outlined"
                password: True
                MDTextFieldHintText:
                    text: "Password"

            MDButton:
                style: "filled"
                size_hint_x: 1
                on_release: root.do_login()
                MDButtonText:
                    text: "Masuk"
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}

            MDButton:
                style: "text"
                pos_hint: {"center_x": 0.5}
                on_release: root.manager.current = 'register'
                MDButtonText:
                    text: "Belum punya akun? Daftar di sini"

<RegisterScreen>:
    name: 'register'
    MDFloatLayout:
        md_bg_color: 0.12, 0.53, 0.90, 1

        MDCard:
            size_hint: 0.88, 0.62
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            elevation: 2
            radius: [20]
            padding: 20
            spacing: 12
            orientation: "vertical"
            md_bg_color: 1, 1, 1, 1

            MDLabel:
                text: "Buat Akun Baru"
                font_style: "Title"
                role: "medium"
                bold: True

            MDTextField:
                id: reg_name
                mode: "outlined"
                MDTextFieldHintText:
                    text: "Nama Lengkap"

            MDTextField:
                id: reg_email
                mode: "outlined"
                MDTextFieldHintText:
                    text: "Email"

            MDTextField:
                id: reg_pass
                mode: "outlined"
                password: True
                MDTextFieldHintText:
                    text: "Password"

            MDButton:
                style: "filled"
                size_hint_x: 1
                on_release: root.do_register()
                MDButtonText:
                    text: "Daftar"
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}

            MDButton:
                style: "text"
                pos_hint: {"center_x": 0.5}
                on_release: root.manager.current = 'login'
                MDButtonText:
                    text: "Sudah punya akun? Login"

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.95, 0.97, 0.99, 1

        MDScreenManager:
            id: inner_manager

            # TAB BERANDA
            MDScreen:
                name: 'tab_beranda'
                MDFloatLayout:
                    MDBoxLayout:
                        orientation: 'vertical'
                        pos_hint: {"top": 1}
                        
                        # Header Kreatif
                        MDBoxLayout:
                            size_hint_y: None
                            height: "120dp"
                            md_bg_color: 0.12, 0.53, 0.90, 1
                            padding: [20, 15, 20, 15]
                            orientation: 'vertical'
                            spacing: 4
                            
                            MDBoxLayout:
                                size_hint_y: None
                                height: "24dp"
                                spacing: 8
                                MDCard:
                                    size_hint: None, None
                                    size: "110dp", "24dp"
                                    md_bg_color: 1, 1, 1, 0.2
                                    radius: [12]
                                    padding: [8, 2, 8, 2]
                                    MDLabel:
                                        id: current_date_lbl
                                        text: "10 Sep 2026"
                                        font_style: "Body"
                                        role: "small"
                                        bold: True
                                        halign: "center"
                                        theme_text_color: "Custom"
                                        text_color: 1, 1, 1, 1

                            MDLabel:
                                id: user_welcome
                                text: "Halo, Budi! 👋"
                                font_style: "Title"
                                role: "large"
                                bold: True
                                theme_text_color: "Custom"
                                text_color: 1, 1, 1, 1

                            MDLabel:
                                id: greeting_sub
                                text: "Siap menyelesaikan targetmu hari ini?"
                                font_style: "Body"
                                role: "medium"
                                theme_text_color: "Custom"
                                text_color: 0.88, 0.94, 1, 1

                        # Toggle Filter
                        MDBoxLayout:
                            size_hint_y: None
                            height: "55dp"
                            padding: [15, 8, 15, 8]
                            spacing: 10
                            
                            MDButton:
                                id: btn_filter_task
                                style: "filled"
                                size_hint_x: 0.5
                                on_release: root.filter_type('task')
                                MDButtonText:
                                    text: "📌 Tugas"
                                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                            MDButton:
                                id: btn_filter_habit
                                style: "outlined"
                                size_hint_x: 0.5
                                on_release: root.filter_type('habit')
                                MDButtonText:
                                    text: "⚡ Kebiasaan"
                                    pos_hint: {"center_x": 0.5, "center_y": 0.5}

                        ScrollView:
                            MDBoxLayout:
                                id: task_container
                                orientation: 'vertical'
                                size_hint_y: None
                                height: self.minimum_height
                                padding: [15, 10, 15, 10]
                                spacing: 10

                    MDFabButton:
                        icon: "plus"
                        pos_hint: {"right": 0.92, "bottom": 0.04}
                        theme_bg_color: "Custom"
                        md_bg_color: 0.12, 0.53, 0.90, 1
                        on_release: root.open_add_dialog()

            # TAB STATISTIK
            MDScreen:
                name: 'tab_statistik'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: 15
                    spacing: 12

                    MDLabel:
                        text: "Statistik & Performa"
                        font_style: "Title"
                        role: "large"
                        bold: True
                        size_hint_y: None
                        height: "30dp"

                    # Card Streak Otomatis
                    MDCard:
                        size_hint_y: None
                        height: "90dp"
                        padding: 15
                        md_bg_color: 1, 0.95, 0.88, 1
                        radius: [15]
                        elevation: 1
                        
                        MDBoxLayout:
                            orientation: 'horizontal'
                            spacing: 15
                            MDIconButton:
                                icon: "fire"
                                icon_size: "40dp"
                                theme_icon_color: "Custom"
                                icon_color: 1, 0.4, 0, 1
                                pos_hint: {"center_y": 0.5}
                            MDBoxLayout:
                                orientation: 'vertical'
                                pos_hint: {"center_y": 0.5}
                                MDLabel:
                                    id: streak_title
                                    text: "🔥 0 Hari Beruntun"
                                    font_style: "Title"
                                    role: "medium"
                                    bold: True
                                    theme_text_color: "Custom"
                                    text_color: 0.8, 0.3, 0, 1
                                MDLabel:
                                    id: streak_sub
                                    text: "Selesaikan tugas hari ini untuk membangun streak!"
                                    font_style: "Body"
                                    role: "small"
                                    theme_text_color: "Custom"
                                    text_color: 0.5, 0.3, 0.1, 1

                    MDLabel:
                        text: "Daftar Riwayat Selesai"
                        font_style: "Title"
                        role: "medium"
                        bold: True
                        size_hint_y: None
                        height: "30dp"

                    ScrollView:
                        MDBoxLayout:
                            id: history_container
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: 8

            # TAB PROFIL
            MDScreen:
                name: 'tab_profil'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: 20
                    spacing: 15
                    pos_hint: {"top": 1}

                    MDLabel:
                        text: "Profil Pengguna"
                        font_style: "Title"
                        role: "large"
                        bold: True
                        size_hint_y: None
                        height: "30dp"

                    MDCard:
                        size_hint_y: None
                        height: "120dp"
                        padding: 15
                        radius: [15]
                        md_bg_color: 1, 1, 1, 1
                        elevation: 1
                        
                        MDBoxLayout:
                            orientation: 'vertical'
                            spacing: 5
                            
                            MDIconButton:
                                icon: "account-circle"
                                icon_size: "48dp"
                                pos_hint: {"center_x": 0.5}
                            MDLabel:
                                id: profile_name
                                text: "Nama User"
                                font_style: "Title"
                                role: "medium"
                                bold: True
                                halign: "center"
                            MDLabel:
                                id: profile_email
                                text: "email@domain.com"
                                font_style: "Body"
                                role: "small"
                                halign: "center"
                                theme_text_color: "Custom"
                                text_color: 0.5, 0.5, 0.5, 1

                    MDButton:
                        style: "filled"
                        pos_hint: {"center_x": 0.5}
                        size_hint_x: 1
                        md_bg_color: 1, 0.35, 0.35, 1
                        on_release: root.logout()
                        MDButtonText:
                            text: "Keluar (Logout)"
                            pos_hint: {"center_x": 0.5, "center_y": 0.5}

        # Bottom Navigation Menyebar Rata
        MDBoxLayout:
            size_hint_y: None
            height: "56dp"
            md_bg_color: 1, 1, 1, 1
            padding: [20, 0, 20, 0]

            MDFloatLayout:
                MDIconButton:
                    icon: "home"
                    pos_hint: {"center_x": 0.1, "center_y": 0.5}
                    on_release: inner_manager.current = 'tab_beranda'

                MDIconButton:
                    icon: "chart-bar"
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    on_release: inner_manager.current = 'tab_statistik'

                MDIconButton:
                    icon: "account"
                    pos_hint: {"center_x": 0.9, "center_y": 0.5}
                    on_release: inner_manager.current = 'tab_profil'
'''

current_user = {"id": None, "name": "", "email": ""}

class LoginScreen(MDScreen):
    def do_login(self):
        email = self.ids.email_input.text
        password = self.ids.pass_input.text
        
        conn = sqlite3.connect('doit.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            global current_user
            current_user["id"] = user[0]
            current_user["name"] = user[1]
            current_user["email"] = user[2]
            
            self.manager.current = 'main'
            self.manager.get_screen('main').on_user_logged_in()
        else:
            self.show_alert("Gagal Login", "Email atau Password salah!")

    def show_alert(self, title, text):
        dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogSupportingText(text=text),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="OK"), on_release=lambda x: dialog.dismiss())
            )
        )
        dialog.open()

class RegisterScreen(MDScreen):
    def do_register(self):
        name = self.ids.reg_name.text
        email = self.ids.reg_email.text
        password = self.ids.reg_pass.text
        
        if name and email and password:
            try:
                conn = sqlite3.connect('doit.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                conn.commit()
                conn.close()
                self.show_alert("Berhasil", "Akun berhasil dibuat! Silakan Login.", to_login=True)
            except sqlite3.IntegrityError:
                self.show_alert("Gagal", "Email ini sudah terdaftar!")
        else:
            self.show_alert("Peringatan", "Harap isi semua kolom!")

    def show_alert(self, title, text, to_login=False):
        def close_dialog(x):
            dialog.dismiss()
            if to_login:
                self.manager.current = 'login'
                
        dialog = MDDialog(
            MDDialogHeadlineText(text=title),
            MDDialogSupportingText(text=text),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="OK"), on_release=close_dialog)
            )
        )
        dialog.open()

class MainScreen(MDScreen):
    dialog = None
    current_filter = 'task'

    def on_user_logged_in(self):
        # Tanggal & Ucapan Dinamis
        today_str = date.today().strftime("%d %b %Y")
        self.ids.current_date_lbl.text = today_str
        
        hour = datetime.now().hour
        greeting = "Selamat Pagi" if hour < 11 else "Selamat Siang" if hour < 15 else "Selamat Sore" if hour < 18 else "Selamat Malam"
        
        self.ids.user_welcome.text = f"{greeting}, {current_user['name'].split()[0]}! 👋"
        self.ids.profile_name.text = current_user['name']
        self.ids.profile_email.text = current_user['email']
        
        self.load_tasks()
        self.calculate_streak()

    def filter_type(self, filter_type):
        self.current_filter = filter_type
        if filter_type == 'task':
            self.ids.btn_filter_task.style = "filled"
            self.ids.btn_filter_habit.style = "outlined"
        else:
            self.ids.btn_filter_task.style = "outlined"
            self.ids.btn_filter_habit.style = "filled"
        self.load_tasks()

    def calculate_streak(self):
        if not current_user["id"]:
            return
            
        conn = sqlite3.connect('doit.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT date_completed FROM tasks WHERE user_id=? AND status=1 AND date_completed IS NOT NULL", (current_user["id"],))
        completed_dates = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Kalkulasi Streak Beruntun
        streak = 0
        check_date = date.today()
        
        while True:
            formatted_date = check_date.strftime("%d %b %Y")
            if formatted_date in completed_dates:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                # Toleransi jika hari ini belum ada yang selesai, periksa hari kemarin
                if check_date == date.today():
                    check_date -= timedelta(days=1)
                    continue
                break

        self.ids.streak_title.text = f"🔥 {streak} Hari Beruntun"
        if streak > 0:
            self.ids.streak_sub.text = "Kerja bagus! Pertahankan konsistensimu!"
        else:
            self.ids.streak_sub.text = "Selesaikan tugas hari ini untuk mulai streak!"

    def load_tasks(self):
        if not current_user["id"]:
            return
            
        conn = sqlite3.connect('doit.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, category FROM tasks WHERE user_id=? AND status=0 AND type=?", 
                       (current_user["id"], self.current_filter))
        active_tasks = cursor.fetchall()
        
        task_container = self.ids.task_container
        task_container.clear_widgets()
        
        for task in active_tasks:
            t_id = task[0]
            
            card = MDCard(
                size_hint_y=None,
                height="65dp",
                radius=[12],
                padding=[10, 5, 10, 5],
                md_bg_color=[1, 1, 1, 1],
                elevation=1
            )
            
            box = MDBoxLayout(orientation='horizontal', spacing=10)
            btn_check = MDIconButton(
                icon="checkbox-blank-outline",
                pos_hint={"center_y": 0.5},
                on_release=lambda x, task_id=t_id: self.complete_task(task_id)
            )
            
            text_box = MDBoxLayout(orientation='vertical', pos_hint={"center_y": 0.5})
            lbl_title = MDLabel(text=task[1], font_style="Title", role="small", bold=True)
            lbl_cat = MDLabel(text=f"• {task[2]}", font_style="Body", role="small", theme_text_color="Custom", text_color=[0.12, 0.53, 0.90, 1])
            text_box.add_widget(lbl_title)
            text_box.add_widget(lbl_cat)
            
            btn_delete = MDIconButton(
                icon="trash-can-outline",
                pos_hint={"center_y": 0.5},
                on_release=lambda x, task_id=t_id: self.delete_task(task_id)
            )
            
            box.add_widget(btn_check)
            box.add_widget(text_box)
            box.add_widget(btn_delete)
            card.add_widget(box)
            task_container.add_widget(card)

        # Load Riwayat Selesai
        cursor.execute("SELECT id, title, date_completed FROM tasks WHERE user_id=? AND status=1", (current_user["id"],))
        completed_tasks = cursor.fetchall()
        
        history_container = self.ids.history_container
        history_container.clear_widgets()
        
        for c_task in completed_tasks:
            c_id = c_task[0]
            
            h_card = MDCard(
                size_hint_y=None,
                height="55dp",
                radius=[10],
                padding=[10, 5, 10, 5],
                md_bg_color=[0.97, 0.98, 1, 1],
                elevation=0
            )
            
            h_box = MDBoxLayout(orientation='horizontal', spacing=10)
            h_icon = MDIconButton(icon="check-circle", theme_icon_color="Custom", icon_color=[0.12, 0.53, 0.90, 1], pos_hint={"center_y": 0.5})
            
            h_text_box = MDBoxLayout(orientation='vertical', pos_hint={"center_y": 0.5})
            h_title = MDLabel(text=c_task[1], font_style="Body", role="medium", bold=True)
            h_date = MDLabel(text=f"Selesai: {c_task[2]}", font_style="Body", role="small", theme_text_color="Custom", text_color=[0.5, 0.5, 0.5, 1])
            h_text_box.add_widget(h_title)
            h_text_box.add_widget(h_date)
            
            h_delete = MDIconButton(icon="trash-can-outline", pos_hint={"center_y": 0.5}, on_release=lambda x, task_id=c_id: self.delete_task(task_id))
            
            h_box.add_widget(h_icon)
            h_box.add_widget(h_text_box)
            h_box.add_widget(h_delete)
            h_card.add_widget(h_box)
            
            history_container.add_widget(h_card)

        conn.close()

    def open_add_dialog(self):
        self.input_field = MDTextField(mode="outlined", size_hint_x=1)
        self.input_field.add_widget(Builder.load_string('MDTextFieldHintText:\n    text: "Nama Tugas / Kebiasaan"'))

        self.category_field = MDTextField(mode="outlined", size_hint_x=1)
        self.category_field.add_widget(Builder.load_string('MDTextFieldHintText:\n    text: "Kategori (Sekolah/Pribadi)"'))

        self.dialog = MDDialog(
            MDDialogHeadlineText(text=f"Tambah {self.current_filter.capitalize()} Baru"),
            MDDialogContentContainer(self.input_field, self.category_field, orientation="vertical", spacing="10dp"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Batal"), on_release=lambda x: self.dialog.dismiss()),
                MDButton(MDButtonText(text="Simpan"), on_release=lambda x: self.save_task()),
                spacing="8dp"
            )
        )
        self.dialog.open()

    def save_task(self):
        title = self.input_field.text
        category = self.category_field.text or "Umum"
        if title and current_user["id"]:
            conn = sqlite3.connect('doit.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (user_id, title, category, type, status) VALUES (?, ?, ?, ?, 0)", 
                           (current_user["id"], title, category, self.current_filter))
            conn.commit()
            conn.close()
            self.dialog.dismiss()
            self.load_tasks()

    def complete_task(self, task_id):
        today = date.today().strftime("%d %b %Y")
        conn = sqlite3.connect('doit.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status = 1, date_completed = ? WHERE id = ?", (today, task_id))
        conn.commit()
        conn.close()
        self.load_tasks()
        self.calculate_streak()

    def delete_task(self, task_id):
        conn = sqlite3.connect('doit.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        self.load_tasks()
        self.calculate_streak()

    def logout(self):
        global current_user
        current_user = {"id": None, "name": "", "email": ""}
        self.manager.current = 'login'

class DoItApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        Builder.load_string(KV)
        
        sm = MDScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    DoItApp().run()