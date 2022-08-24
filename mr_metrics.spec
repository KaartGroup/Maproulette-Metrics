# -*- mode: python -*-

import platform
import re
from os.path import isfile

is_mac = platform.system().lower() == "darwin"

block_cipher = None


a = Analysis(
    ["entrypoint.py"],
    pathex=[],
    binaries=[],
    # datas=added_files,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=["ptvsd"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
items = (
    []
    if is_mac
    else [
        a.binaries,
        a.zipfiles,
        a.datas,
    ]
)
exe = EXE(
    pyz,
    a.scripts,
    *items,
    [],
    exclude_binaries=is_mac,
    name="Maproulette Metrics",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    icon=None if is_mac else None,
)
if is_mac:
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        name="Maproulette Metrics",
    )
    app = BUNDLE(
        coll,
        name="Maproulette Metrics.app",
        icon=None,
        bundle_identifier="com.kaart.mr_metrics",
        info_plist={
            "NSHighResolutionCapable": "True",
            # "CFBundleVersion": APP_VERSION,
            # "CFBundleShortVersionString": APP_VERSION,
        },
    )
