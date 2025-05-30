import whisper
import os

# Konstanta global untuk menyimpan nama model Whisper yang valid.
# Digunakan untuk validasi input dan pengisian dropdown di GUI.
AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

def format_timestamp(seconds: float) -> str:
    """
    Mengonversi total detik dalam format float ke format timestamp SRT (HH:MM:SS,ms).

    Args:
        seconds (float): Waktu dalam detik yang akan diformat.

    Returns:
        str: String timestamp yang sudah diformat sesuai standar SRT.
    """
    # Memastikan input tidak negatif untuk menghindari error perhitungan.
    assert seconds >= 0, "non-negative timestamp expected"
    
    # Konversi detik ke milidetik untuk perhitungan yang lebih mudah.
    milliseconds = round(seconds * 1000.0)

    # Gunakan divmod untuk mendapatkan jam dan sisa milidetik secara efisien.
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds = milliseconds // 1_000
    milliseconds %= 1_000

    # Format output string dengan padding nol agar sesuai standar (misal: 01, 007).
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def transcribe_audio(file_path: str, model_name: str, progress_signal=None):
    """
    Fungsi utama untuk melakukan transkripsi pada file audio/video.
    Fungsi ini juga akan membuat file .srt secara otomatis dan melaporkan progresnya 
    kembali ke GUI melalui sinyal PyQt.

    Args:
        file_path (str): Path absolut ke file audio atau video yang akan diproses.
        model_name (str): Nama model Whisper yang akan digunakan (harus ada di AVAILABLE_MODELS).
        progress_signal (pyqtSignal, optional): Objek sinyal dari PyQt untuk mengirim progres. Defaults to None.

    Returns:
        tuple: Sebuah tuple berisi (string_transkripsi_penuh, path_ke_file_srt).
    """
    
    # Fungsi helper internal untuk mengirim sinyal progres dengan aman.
    # Ini mencegah error jika fungsi dijalankan tanpa GUI (misal, saat testing).
    def report_progress(percent, message):
        if progress_signal:
            progress_signal.emit(percent, message)

    # Melaporkan tahap awal proses ke GUI.
    report_progress(10, f"Mempersiapkan model '{model_name}'...")
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Model '{model_name}' tidak tersedia.")

    # Memuat model Whisper. Proses ini bisa memakan waktu dan memori yang signifikan,
    # terutama saat pertama kali dijalankan karena model perlu diunduh.
    model = whisper.load_model(model_name)
    report_progress(30, f"Model '{model_name}' dimuat. Memulai transkripsi...")

    # Menjalankan proses transkripsi utama.
    # 'fp16=False' digunakan untuk kompatibilitas CPU yang lebih luas.
    # 'verbose=False' untuk mencegah Whisper mencetak log progresnya sendiri ke konsol.
    result = model.transcribe(file_path, fp16=False, verbose=False)
    report_progress(60, "Transkripsi audio selesai. Memformat output...")

    # Menentukan nama dan path file output .srt.
    # Dibuat di direktori yang sama dengan file input dengan mengganti ekstensinya.
    output_srt_path = os.path.splitext(file_path)[0] + ".srt"
    
    # Membuka file .srt untuk ditulis dan melakukan iterasi pada hasil transkripsi.
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        # 'result["segments"]' berisi daftar segmen teks beserta waktu mulai dan selesainya.
        for i, segment in enumerate(result["segments"]):
            # Menulis setiap blok subtitle sesuai format standar SRT.
            # 1. Nomor urut
            srt_file.write(f"{i + 1}\n")
            # 2. Timestamp (Mulai --> Selesai)
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            srt_file.write(f"{start_time} --> {end_time}\n")
            # 3. Teks subtitle
            srt_file.write(f"{segment['text'].strip()}\n\n")

    # Melaporkan bahwa proses penyimpanan file telah selesai.
    report_progress(95, f"File SRT disimpan di: {output_srt_path}")
    
    # Mengembalikan hasil akhir sebagai tuple yang akan digunakan oleh GUI.
    return (result["text"], output_srt_path)