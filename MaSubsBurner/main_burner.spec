# main_burner.spec (versi final dengan ffmpeg terbundel)
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main_burner.py'],
    pathex=[],
    # --- PERUBAHAN PENTING ADA DI SINI ---
    # Beritahu PyInstaller untuk menambahkan ffmpeg.exe dan ffprobe.exe
    binaries=[('ffmpeg.exe', '.'), ('ffprobe.exe', '.')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='MaSubsBurner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_hooks=[],
    excludes=[],
    windowed=True,
    icon='logo_burner.ico', # Ganti nama ikon jika perlu
)