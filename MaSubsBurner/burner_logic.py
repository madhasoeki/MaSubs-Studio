import ffmpeg
import os
import sys

def get_ffmpeg_path():
    """
    Menentukan path yang benar untuk executable ffmpeg.
    Fungsi ini memungkinkan skrip untuk bekerja baik dalam mode pengembangan (menjalankan file .py)
    maupun dalam mode produksi (menjalankan file .exe yang sudah dibundel).
    
    Returns:
        str: Path absolut ke 'ffmpeg.exe' jika dibundel, atau string 'ffmpeg' jika tidak.
    """
    # 'getattr(sys, 'frozen', False)' adalah cara standar untuk memeriksa apakah skrip
    # sedang berjalan sebagai paket PyInstaller yang "dibekukan".
    if getattr(sys, 'frozen', False):
        # Jika ya, 'sys._MEIPASS' berisi path ke direktori sementara
        # tempat semua file (termasuk ffmpeg.exe yang kita bundel) diekstrak.
        application_path = sys._MEIPASS
        return os.path.join(application_path, 'ffmpeg.exe')
    else:
        # Jika tidak (berjalan sebagai skrip .py biasa), kita asumsikan 'ffmpeg'
        # sudah ada di sistem PATH untuk kemudahan pengembangan.
        return 'ffmpeg'

def burn_subtitles(video_path: str, subtitle_path: str, output_path: str):
    """
    Fungsi utama untuk 'membakar' (hardcode) file subtitle ke dalam file video.
    Menggunakan pustaka ffmpeg-python untuk membangun dan menjalankan perintah FFmpeg.

    Args:
        video_path (str): Path ke file video sumber.
        subtitle_path (str): Path ke file subtitle (.srt).
        output_path (str): Path untuk menyimpan file video hasil.

    Returns:
        tuple: Sebuah tuple (bool, str) yang berisi status keberhasilan dan pesan.
               Contoh: (True, "Proses berhasil...") atau (False, "Error: ...").
    """
    try:
        # Filter 'subtitles' pada FFmpeg lebih andal dengan forward slashes, 
        # terutama saat berjalan di lingkungan Windows.
        subtitle_path_clean = subtitle_path.replace('\\', '/')
        
        # Mendapatkan path ffmpeg.exe yang akan digunakan (bisa dari bundel atau PATH sistem).
        ffmpeg_executable = get_ffmpeg_path()

        # Membangun grafik pemrosesan FFmpeg.
        # 1. Tentukan input stream dari file video.
        input_stream = ffmpeg.input(video_path)
        
        # 2. Pisahkan stream video dan audio untuk diproses secara terpisah.
        video_stream = input_stream['v']
        audio_stream = input_stream['a']

        # 3. Terapkan filter 'subtitles' HANYA pada stream video.
        video_with_subs = ffmpeg.filter(
            video_stream, 'subtitles', filename=subtitle_path_clean
        )

        # 4. Tentukan output, gabungkan kembali stream video (yang sudah ada subtitle)
        #    dan stream audio asli ke dalam satu file output.
        stream = ffmpeg.output(
            video_with_subs, 
            audio_stream, 
            output_path,
            # Pengaturan encoding:
            vcodec='libx264',    # Codec video H.264 yang sangat umum dan kompatibel.
            crf=23,              # Constant Rate Factor, kualitas visual yang baik (default).
            preset='veryfast',   # Keseimbangan yang baik antara kecepatan encoding dan ukuran file.
            acodec='aac',        # Codec audio AAC, standar untuk kontainer MP4.
            audio_bitrate='192k' # Bitrate audio yang umum untuk kualitas stereo yang baik.
        )
        
        # 5. Jalankan perintah FFmpeg yang telah dibangun.
        #    'cmd' secara eksplisit menunjuk ke executable ffmpeg yang benar.
        #    'quiet=True' mencegah FFmpeg mencetak log progresnya ke konsol.
        #    'overwrite_output=True' otomatis menimpa file output jika sudah ada.
        ffmpeg.run(stream, cmd=ffmpeg_executable, quiet=True, overwrite_output=True)
        
        # Jika proses berhasil tanpa error, kembalikan status sukses.
        return True, f"Proses berhasil. File disimpan di {output_path}"

    # Menangani error yang spesifik dari eksekusi FFmpeg.
    except ffmpeg.Error as e:
        # 'e.stderr.decode()' memberikan pesan error yang lebih detail langsung dari FFmpeg.
        error_details = e.stderr.decode() if e.stderr else "Tidak ada detail error dari ffmpeg."
        print(f"FFmpeg Error:\n{error_details}", file=sys.stderr)
        return False, f"FFmpeg Error: {error_details}"
    # Menangani error Python umum lainnya yang mungkin terjadi.
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return False, f"An unexpected error occurred: {e}"

# Blok ini hanya akan dieksekusi jika file 'burner_logic.py' dijalankan secara langsung.
# Berguna untuk melakukan pengetesan cepat pada fungsi 'burn_subtitles'.
if __name__ == '__main__':
    print("--- Memulai Proses Pengetesan Burn-in Subtitle ---")
    
    # Pengembang perlu mengubah path di bawah ini untuk melakukan testing.
    test_video = "PATH_TO_YOUR_VIDEO.mp4"
    test_srt = "PATH_TO_YOUR_SUBTITLE.srt"
    test_output = "video_hardsub_output.mp4"

    # Validasi sederhana untuk memastikan file testing ada.
    if not os.path.exists(test_video) or not os.path.exists(test_srt):
        print("\n[ERROR] File video atau subtitle untuk testing tidak ditemukan.")
        print("Harap ubah path variabel 'test_video' dan 'test_srt' di dalam script burner_logic.py.")
    else:
        print(f"Video Input: {test_video}")
        print(f"Subtitle Input: {test_srt}")
        print(f"Output Akan Disimpan Sebagai: {test_output}")
        print("\nMemulai proses... Ini mungkin memakan waktu beberapa saat.")
        
        # Memanggil fungsi utama untuk testing.
        success, message = burn_subtitles(test_video, test_srt, test_output)
        
        # Mencetak hasil testing ke konsol.
        if success:
            print(f"\n[SUKSES] {message}")
        else:
            print(f"\n[GAGAL] {message}")