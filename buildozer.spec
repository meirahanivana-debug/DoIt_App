[app]

# (str) Title of your application
title = DoIt

# (str) Package name
package.name = doit

# (str) Package domain (needed for android packaging)
package.domain = org.doit

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,db

# (list) List of inclusions using pattern matching
source.include_patterns = avatars/*,*.png,*.kv,*.db

# (list) Application requirements
# PENTING: sqlite3 dihapus dari sini karena bawaan Python. Ditambahkan pillow untuk gambar.
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,plyer

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (list) Permissions
android.permissions = VIBRATE, POST_NOTIFICATIONS, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (bool) Accept SDK license
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1