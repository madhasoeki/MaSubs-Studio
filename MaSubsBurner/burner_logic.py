import ffmpeg
import os
import sys

def get_ffmpeg_path():
    """
    Fungsi cerdas untuk menemukan path ffmpeg.
    Jika dijalankan sebagai .exe dari PyInstaller, ia akan mencari di dalam folder sementara.
    Jika dijalankan sebagai skrip .py biasa, ia akan menggunakan 'ffmpeg' dari PATH.
    """
    if getattr(sys, 'frozen', False):
        # Berjalan sebagai .exe yang dibundel
        # sys._MEIPASS adalah path ke folder sementara tempat PyInstaller mengekstrak semuanya
        application_path = sys._MEIPASS
        return os.path.join(application_path, 'ffmpeg.exe')
    else:
        # Berjalan sebagai skrip .py biasa
        # Asumsikan ffmpeg ada di PATH untuk kemudahan pengembangan
        return 'ffmpeg'

def burn_subtitles(video_path: str, subtitle_path: str, output_path: str):
    """
    Fungsi untuk 'membakar' subtitle ke dalam video menggunakan ffmpeg-python.
    """
    try:
        subtitle_path_clean = subtitle_path.replace('\\', '/')
        ffmpeg_executable = get_ffmpeg_path() # Panggil fungsi cerdas kita
        print(f"Using ffmpeg from: {ffmpeg_executable}") # Untuk debug

        input_stream = ffmpeg.input(video_path)
        video_stream = input_stream['v']
        audio_stream = input_stream['a']

        video_with_subs = ffmpeg.filter(
            video_stream, 'subtitles', filename=subtitle_path_clean,
        )

        stream = ffmpeg.output(
            video_with_subs, audio_stream, output_path, y=None,
            vcodec='libx264', crf=23, preset='veryfast',
            acodec='aac', audio_bitrate='192k'
        )
        
        ffmpeg.run(stream, cmd=ffmpeg_executable, quiet=True, overwrite_output=True)
        
        return True, f"Proses berhasil. File disimpan di {output_path}"

    except ffmpeg.Error as e:
        error_details = e.stderr.decode() if e.stderr else "Tidak ada detail error dari ffmpeg."
        print(f"FFmpeg Error:\n{error_details}", file=sys.stderr)
        return False, f"FFmpeg Error: {error_details}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return False, f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    print("--- Memulai Proses Pengetesan Burn-in Subtitle ---")
    
    test_video = "PATH_TO_YOUR_VIDEO.mp4"
    test_srt = "PATH_TO_YOUR_SUBTITLE.srt"
    test_output = "video_hardsub_output.mp4"

    if not os.path.exists(test_video) or not os.path.exists(test_srt):
        print("\n[ERROR] File video atau subtitle untuk testing tidak ditemukan.")
        print("Harap ubah path variabel 'test_video' dan 'test_srt' di dalam script burner_logic.py.")
    else:
        print(f"Video Input: {test_video}")
        print(f"Subtitle Input: {test_srt}")
        print(f"Output Akan Disimpan Sebagai: {test_output}")
        print("\nMemulai proses... Ini mungkin memakan waktu beberapa saat.")
        
        success, message = burn_subtitles(test_video, test_srt, test_output)
        
        if success:
            print(f"\n[SUKSES] {message}")
        else:
            print(f"\n[GAGAL] {message}")