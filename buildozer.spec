[app]
title = دستیار املاک
package.name = realestate
package.domain = ir.realestate
source.dir = .
source.include_exts = py,png,jpg,jpeg,ttf,otf
version = 1.0.0
requirements = python3,kivy==2.3.1,arabic-reshaper,python-bidi
orientation = portrait
fullscreen = 0
android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.skip_update = True
p4a.bootstrap = sdl2
p4a.extra_args = --no-report

[buildozer]
log_level = 2
warn_on_root = 1