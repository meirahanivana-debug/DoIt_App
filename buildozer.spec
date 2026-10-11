[app]
title = Doit
package.name = doitapp
package.domain = org.doit
source.dir = .
source.include_exts = py,png,kv
source.include_patterns = *.kv,avatars/*
source.exclude_patterns = image.png,*.db
version = 0.8
requirements = python3,kivy==2.3.0,kivymd==1.2.0,plyer,pillow
orientation = portrait
fullscreen = 1
icon.filename = %(source.dir)s/logo_doit.png
presplash.filename = %(source.dir)s/logo_doit.png
p4a.branch = v2024.01.21

# Android Configurations
android.permissions = android.permission.POST_NOTIFICATIONS, android.permission.RECEIVE_BOOT_COMPLETED, android.permission.SCHEDULE_EXACT_ALARM
android.add_src = android_src
android.extra_manifest_xml = android_manifest.xml
p4a.hook = android_hook.py
android.api = 34
android.minapi = 21
android.package_format = apk

[buildozer]
log_level = 2
warn_on_root = 1
