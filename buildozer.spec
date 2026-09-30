[app]
title = Doit
package.name = doitapp
package.domain = org.doit
source.dir = .
source.include_exts = py,png,kv,db
source.include_patterns = *.kv,*.png,*.db,avatars/*
version = 0.1
requirements = python3,kivy,kivymd,plyer,pillow
orientation = portrait
fullscreen = 1

# Android Configurations
android.permissions = android.permission.POST_NOTIFICATIONS
android.api = 34
android.minapi = 21
android.skip_build_oz = False
android.package_format = apk

[buildozer]
log_level = 2
warn_on_root = 1
