# core_logic.py (versi 4 - dengan laporan progres)
import whisper
import os

AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

def format_timestamp(seconds: float) -> str:
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds = milliseconds // 1_000
    milliseconds %= 1_000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

# PERUBAHAN: Fungsi ini sekarang menerima 'progress_signal'
def transcribe_audio(file_path: str, model_name: str, progress_signal=None):
    """
    Melakukan transkripsi dan melaporkan progres melalui sinyal yang diberikan.
    """
    def report_progress(percent, message):
        if progress_signal:
            progress_signal.emit(percent, message)

    report_progress(10, f"Mempersiapkan model '{model_name}'...")
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Model '{model_name}' tidak tersedia.")

    model = whisper.load_model(model_name)
    report_progress(30, f"Model '{model_name}' dimuat. Memulai transkripsi...")

    result = model.transcribe(file_path, fp16=False, verbose=False)
    report_progress(60, "Transkripsi audio selesai. Memformat output...")

    output_srt_path = os.path.splitext(file_path)[0] + ".srt"
    
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        for i, segment in enumerate(result["segments"]):
            srt_file.write(f"{i + 1}\n")
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            srt_file.write(f"{start_time} --> {end_time}\n")
            srt_file.write(f"{segment['text'].strip()}\n\n")

    report_progress(95, f"File SRT disimpan di: {output_srt_path}")
    return (result["text"], output_srt_path)