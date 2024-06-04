# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = []
datas += copy_metadata('readchar')
datas += copy_metadata('python-pcapng')
datas += copy_metadata('apple_compress')
datas += copy_metadata('pyimg4')


a = Analysis(
    ['pymobiledevice3/__main__.py'],
    pathex=[],
    binaries=[('/Users/yzx/出海工具/pymobiledevice3/pymobiledevice3/resources/webinspector', 'pymobiledevice3/resources/webinspector')],
    datas=datas,
    hiddenimports=['pymobiledevice3.cli', 'readchar', 'apple_compress'],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mobdevice',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mobdevice',
)
