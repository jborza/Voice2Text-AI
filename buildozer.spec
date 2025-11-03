[app]

# (str) Title of your application
title = Voice 2 Text

# (str) Package name
package.name = voice2text

# (str) Package domain (needed for android/ios packaging)
package.domain = com.voice2text

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
source.include_patterns = voice_app_kivy.py,requirements.txt

# (list) Source files to exclude (use wildcards if needed)
source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = __pycache__,bin,.git

# (list) List of exclusions using pattern matching
source.exclude_patterns = voice_app.py,*.spec,*.md,*.yml,*.yaml,*.txt,*.sh

# (str) Application versioning (method 1)
version = 0.1

# (str) Application versioning (method 2)
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# (list) Application requirements
requirements = kivy,requests,gtts,pygame,numpy,torch,faster-whisper,scipy

# (str) Custom source folders for requirements
requirements.source.kivy =

# (list) Garden requirements
garden_requirements =

# (str) Presplash of the application
presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info

# iOS specific
#

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#     [app]
#     source.exclude_patterns = license,*.pyc
#
#    This can also be translated into:
#
#     [app:source.exclude_patterns]
#     license
#     *.pyc

#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you can define:
#
#     [app]
#     orientation = all
#
#     [app:portrait]
#     orientation = portrait