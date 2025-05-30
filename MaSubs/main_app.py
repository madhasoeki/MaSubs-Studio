import sys
import os

# --- BLOK KODE UNTUK MEMBUNDEL FFMPEG ---
# Blok ini sangat penting agar aplikasi yang sudah menjadi .exe dapat menemukan ffmpeg.
# 'sys.frozen' bernilai True hanya ketika skrip dijalankan sebagai paket PyInstaller.
if getattr(sys, 'frozen', False):
    # 'sys._MEIPASS' adalah path ke folder sementara tempat PyInstaller mengekstrak semua file.
    application_path = sys._MEIPASS
    # Kita menambahkan path ini ke awal dari environment variable 'PATH'.
    # Ini memastikan pustaka 'whisper' akan menemukan 'ffmpeg.exe' yang kita bundel
    # sebelum mencarinya di tempat lain di sistem.
    os.environ['PATH'] = application_path + os.pathsep + os.environ.get('PATH', '')

# --- Impor Pustaka ---
# Impor komponen-komponen yang dibutuhkan dari PyQt6 untuk membangun GUI.
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit, QStatusBar,
    QFileDialog, QMessageBox, QProgressBar
)
# Impor komponen inti PyQt6 untuk threading dan sinyal.
from PyQt6.QtCore import QThread, QObject, pyqtSignal
# Impor untuk ikon aplikasi.
from PyQt6.QtGui import QIcon
# Impor fungsi logika inti dan konstanta dari file lokal.
from core_logic import transcribe_audio, AVAILABLE_MODELS


# --- Kelas Worker untuk Threading ---
class Worker(QObject):
    """
    Kelas ini menangani tugas berat (transkripsi) di thread terpisah.
    Ini mencegah GUI menjadi 'freeze' atau 'not responding' selama proses berjalan.
    Kelas ini tidak boleh memanipulasi GUI secara langsung, melainkan berkomunikasi
    melalui sinyal (signals).
    """
    # Sinyal untuk berkomunikasi dengan thread utama (GUI).
    # 'finished' akan mengirim tuple berisi (hasil_teks, path_srt) saat selesai.
    finished = pyqtSignal(tuple)
    # 'error' akan mengirim pesan error jika terjadi kegagalan.
    error = pyqtSignal(str)
    # 'progress' akan mengirim update (persentase, pesan) selama proses berjalan.
    progress = pyqtSignal(int, str)

    def __init__(self, file_path, model_name):
        super().__init__()
        # Menyimpan informasi yang dibutuhkan untuk tugas dari thread utama.
        self.file_path = file_path
        self.model_name = model_name

    def run(self):
        """
        Metode ini adalah titik masuk untuk eksekusi di thread terpisah.
        Semua logika yang memakan waktu lama ditempatkan di sini.
        """
        try:
            # Memanggil fungsi transkripsi dari core_logic dan melewatkan sinyal progress.
            result_tuple = transcribe_audio(self.file_path, self.model_name, self.progress)
            # Jika berhasil, kirim sinyal 'finished' beserta hasilnya.
            self.finished.emit(result_tuple)
        except Exception as e:
            # Jika terjadi error apapun selama proses, tangkap dan kirim sinyal 'error'.
            self.error.emit(str(e))

# --- Kelas Utama Aplikasi ---
class MaSubsApp(QMainWindow):
    """
    Kelas utama aplikasi yang bertindak sebagai jendela utama (QMainWindow).
    Mengelola semua widget GUI, koneksi sinyal-slot, dan orkestrasi thread.
    """
    def __init__(self):
        super().__init__()
        
        # Properti untuk menyimpan path file yang dipilih oleh pengguna.
        self.selected_file_path = None
        
        # Panggil metode untuk menginisialisasi dan mengatur semua elemen UI.
        self.init_ui()

    def init_ui(self):
        """Menginisialisasi semua komponen antarmuka pengguna (UI)."""
        self.setWindowTitle("MaSubs - Auto Subtitle Generator")
        if os.path.exists("logo.ico"):
            self.setWindowIcon(QIcon("logo.ico"))
        self.setGeometry(100, 100, 700, 500)

        # Widget pusat dan layout utama untuk menampung semua elemen lain.
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # --- Bagian UI: Pemilihan File ---
        self.btn_browse = QPushButton("1. Pilih File Audio/Video...")
        self.btn_browse.clicked.connect(self.open_file_dialog) # Menghubungkan klik tombol ke metode.
        self.layout.addWidget(self.btn_browse)

        self.lbl_file_path = QLabel("Belum ada file yang dipilih.")
        self.lbl_file_path.setStyleSheet("font-style: italic; color: grey;")
        self.layout.addWidget(self.lbl_file_path)

        # --- Bagian UI: Pemilihan Model ---
        self.lbl_model = QLabel("2. Pilih Model Transkripsi:")
        self.layout.addWidget(self.lbl_model)

        self.combo_model = QComboBox()
        self.combo_model.addItems(AVAILABLE_MODELS)
        self.combo_model.setCurrentText("base") # Set nilai default.
        self.layout.addWidget(self.combo_model)

        # --- Bagian UI: Indikator Progres ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False) # Sembunyikan sampai proses dimulai.
        self.layout.addWidget(self.progress_bar)
        
        # --- Bagian UI: Tombol Aksi ---
        self.btn_start = QPushButton("3. Mulai Transkripsi")
        self.btn_start.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")
        self.btn_start.clicked.connect(self.start_transcription)
        self.layout.addWidget(self.btn_start)

        # --- Bagian UI: Area Hasil ---
        self.lbl_result = QLabel("Hasil Transkripsi:")
        self.layout.addWidget(self.lbl_result)

        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True) # Agar pengguna tidak bisa mengedit hasil.
        self.layout.addWidget(self.text_result)

        # --- Status Bar di bagian bawah jendela ---
        self.setStatusBar(QStatusBar(self))
        self.update_status("Siap")
        
    def start_transcription(self):
        """Metode ini dipanggil saat tombol 'Mulai Transkripsi' diklik."""
        # 1. Validasi: Pastikan pengguna sudah memilih file.
        if not self.selected_file_path:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih file terlebih dahulu!")
            return

        # 2. Persiapan UI: Nonaktifkan tombol untuk mencegah klik ganda dan siapkan area progres.
        self.btn_start.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.text_result.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 3. Dapatkan input dari pengguna (model yang dipilih).
        selected_model = self.combo_model.currentText()
        
        # 4. Inisialisasi Threading: Buat objek thread dan worker.
        self.thread = QThread()
        self.worker = Worker(self.selected_file_path, selected_model)
        self.worker.moveToThread(self.thread) # Pindahkan worker ke thread baru.

        # 5. Hubungkan Sinyal ke Slot: Ini adalah inti dari komunikasi antar-thread.
        #    - Saat thread dimulai, jalankan metode 'run' dari worker.
        #    - Jika worker mengirim sinyal 'finished', panggil metode 'on_transcription_finished'.
        #    - Jika worker mengirim sinyal 'error', panggil metode 'on_transcription_error'.
        #    - Jika worker mengirim sinyal 'progress', panggil metode 'update_progress'.
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_transcription_finished)
        self.worker.error.connect(self.on_transcription_error)
        self.worker.progress.connect(self.update_progress)

        # 6. Atur pembersihan (cleanup) setelah thread selesai.
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        # 7. Mulai eksekusi thread. Proses 'run' di worker akan dimulai.
        self.thread.start()

    def update_progress(self, percent, message):
        """Slot yang menerima sinyal progres dan memperbarui UI."""
        self.progress_bar.setValue(percent)
        self.update_status(message)

    def on_transcription_finished(self, result_tuple):
        """Slot yang menerima sinyal 'finished' dan menampilkan hasil."""
        self.progress_bar.setValue(100)
        self.update_status("Transkripsi Selesai!")

        plain_text, saved_path = result_tuple
        self.text_result.setText(plain_text)
        
        QMessageBox.information(self, "Sukses", f"Proses transkripsi telah selesai!\n\nFile subtitle disimpan di:\n{saved_path}")
        
        # Aktifkan kembali UI setelah proses selesai.
        self.btn_start.setEnabled(True)
        self.btn_browse.setEnabled(True)
        self.progress_bar.setVisible(False)

    def on_transcription_error(self, error_message):
        """Slot yang menerima sinyal 'error' dan menampilkan pesan kesalahan."""
        self.progress_bar.setVisible(False)
        self.update_status(f"Error!")
        QMessageBox.critical(self, "Error", f"Terjadi kesalahan:\n{error_message}")
        
        # Aktifkan kembali UI setelah terjadi error.
        self.btn_start.setEnabled(True)
        self.btn_browse.setEnabled(True)

    def open_file_dialog(self):
        """Membuka dialog file sistem untuk memilih file input."""
        # 'QFileDialog.getOpenFileName' mengembalikan tuple (nama_file, filter_dipilih).
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih File Audio/Video", "", "All Files (*);;Audio Files (*.mp3 *.wav *.m4a);;Video Files (*.mp4 *.mkv)")
        if file_name:
            self.selected_file_path = file_name
            self.lbl_file_path.setText(f"File: {file_name}")
            self.lbl_file_path.setStyleSheet("font-style: normal; color: black;")
            self.update_status(f"File dipilih: {file_name}")
            
    def update_status(self, message):
        """Metode utilitas untuk menampilkan pesan di status bar."""
        self.statusBar().showMessage(message)

# --- Titik Masuk Eksekusi Aplikasi ---
# '__name__ == "__main__"' memastikan kode ini hanya berjalan saat file ini dieksekusi secara langsung.
if __name__ == '__main__':
    # Membuat instance aplikasi utama.
    app = QApplication(sys.argv)
    # Membuat instance dari kelas jendela utama kita.
    window = MaSubsApp()
    # Menampilkan jendela ke layar.
    window.show()
    # Memulai event loop aplikasi dan menunggu interaksi pengguna.
    sys.exit(app.exec())