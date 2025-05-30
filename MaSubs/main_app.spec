# main_app.spec (versi final dengan whisper assets DAN ffmpeg)
# -*- mode: python ; coding: utf-8 -*-

# Path ke aset whisper (pastikan path ini benar)
whisper_assets_path = r'D:\Ramadhan\python\MaSubs\venv\Lib\site-packages\whisper\assets'


a = Analysis(
    ['main_app.py'],
    pathex=[],
    # --- PERUBAHAN PENTING ADA DI SINI ---
    # Kita tambahkan ffmpeg.exe dan ffprobe.exe ke daftar binaries
    binaries=[('ffmpeg.exe', '.'), ('ffprobe.exe', '.')],
    # 'datas' dari perbaikan sebelumnya tetap ada
    datas=[(whisper_assets_path, 'whisper/assets')],
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
    name='MaSubs',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_hooks=[],
    excludes=[],
    windowed=True,
    icon='logo.ico',
)