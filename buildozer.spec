[app]
title = Universal Downloader Pro
package.name = univdownloader
package.domain = com.sifat
source.dir = .
source.include_exts = py,png,jpg
version = 0.1
requirements = python3,kivy,yt-dlp,jnius,openssl
icon.filename = %(source.dir)s/my_logo.png
orientation = portrait
fullscreen = 1

android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a, armeabi-v7a
android.skip_byte_compile = 1

[buildozer]
log_level = 2
warn_on_root = 0
