[app]

# (str) Title of your application
title = AnkiDroid

# (str) Package name
package.name = ankidroid

# (str) Package domain (needed for android/ios packaging)
package.domain = org.ankidroid

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let the packaging system know what to
# include)
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*, data/*.json

# (list) Source files to exclude (let the packaging system know what to
# not include)
#source.exclude_exts = spec

# (list) List of directory to exclude (let the packaging system know what to
# not include)
#source.exclude_dirs = tests, bin

# (list) List of additional files to include (see string above)
#source.includes =

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1,kivymd==1.2.0

# (str) Custom source folders for requirements
#requirements.source.kivy = ../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/splash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY, NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author = ©2025 Anton

# (str) Application authoring author
author = Anton

# (str) Application authoring email
#author.email =

# (str) Application authoring website
#author.website =

#
# Android Specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Supported Android API level
android.api = 33

# (int) Minimum API level
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 24

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use Android's private external storage directory to store data
android.private_storage = True

# (bool) Use Android's shared storage for app data
#android.shared_storage = False

# (str) Android permissions
android.permissions = INTERNET

# (list) Android extra Java dependencies
#android.add_src =

# (str) Android extra Java jars
#android.add_jars = foo.jar,bar.jar

# (str) AntryPoint for the application
android.entrypoint = main.py

# (list) List of Java .class files to add to the project
#android.add_classes =

# (list) List of Java files to add to the project
#android.add_aidl =

# (list) Android libraries to prebuild
#android.library_references =

# (str) The Android logcat filter
#android.logcat_filters =

# (int) Android logging level (5 = Verbose, 4 = Debug, 3 = Info, 2 = Warning, 1 = Error)
#android.log_level = 2

# (bool) Copy library instead of making a libsymlink
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (int) The Android app theme
#android.theme = @android:style/Theme.Material.Light

#
# iOS Specific
#

# (str) iOS application title
#ios.title = AnkiDroid

# (str) iOS application package name
#ios.package_name = ankidroid

# (str) iOS application version
#ios.version = 0.1

# (bool) Enable iOS capabilities
#ios.capabilities =

#
# Windows Specific
#

# (str) Windows application version
#win.version = 1.0

#
# macOS Specific
#

# (str) macOS application version
#osx.version = 1.0

#
# Linux Specific
#

# (str) Linux application version
#linux.version = 1.0

# (list) Linux desktop integration
#linux.desktop = True
