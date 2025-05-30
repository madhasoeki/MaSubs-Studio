# cari_path.py
import whisper
import os

# Menemukan direktori tempat pustaka whisper diinstal
whisper_dir = os.path.dirname(whisper.__file__)

# Membuat path ke folder assets di dalamnya
assets_path = os.path.join(whisper_dir, 'assets')

print("Salin dan gunakan path di bawah ini untuk file .spec Anda:")
print(assets_path)