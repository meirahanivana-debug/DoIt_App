[app]

# (str) Title of your application
title = DoIt

# (str) Package name
package.name = doit

# (str) Package domain (needed for android packaging)
package.domain = org.doit

# (list) Source files to include (let empty to include all files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
requirements = python3,kivy,kivymd,sqlite3,plyer

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (list) Permissions
android.permissions = VIBRATE, POST_NOTIFICATIONS

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21