import sys
import os

# --- Impor Pustaka ---
# Impor komponen-komponen yang dibutuhkan dari PyQt6 untuk membangun GUI.
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QProgressBar, QStatusBar,
    QFileDialog, QMessageBox
)
# Impor untuk ikon aplikasi.
from PyQt6.QtGui import QIcon
# Impor komponen inti PyQt6 untuk threading dan sinyal.
from PyQt6.QtCore import QThread, QObject, pyqtSignal

# Impor fungsi logika inti dari file lokal.
from burner_logic import burn_subtitles


# --- Kelas Worker untuk Threading ---
class Worker(QObject):
    """
    Menjalankan tugas berat (proses burn-in video) di thread terpisah
    untuk mencegah GUI menjadi 'freeze'. Berkomunikasi dengan thread utama
    melalui sinyal (signals).
    """
    # Sinyal untuk komunikasi:
    # 'finished' akan mengirimkan tuple (status_sukses, pesan_hasil) saat selesai.
    finished = pyqtSignal(tuple)
    # 'error' akan mengirimkan pesan jika terjadi kegagalan tak terduga.
    error = pyqtSignal(str)
    # 'progress' bisa digunakan di masa depan untuk mengirim update status (saat ini tidak dipakai).
    progress = pyqtSignal(str)

    def __init__(self, video_path, subtitle_path, output_path):
        super().__init__()
        # Menyimpan semua path yang dibutuhkan untuk proses burning.
        self.video_path = video_path
        self.subtitle_path = subtitle_path
        self.output_path = output_path

    def run(self):
        """
        Metode ini dieksekusi di dalam thread terpisah saat thread.start() dipanggil.
        """
        try:
            # Memanggil fungsi inti yang memakan waktu lama dari burner_logic.
            success, message = burn_subtitles(self.video_path, self.subtitle_path, self.output_path)
            # Mengirim sinyal 'finished' beserta hasilnya kembali ke thread utama.
            self.finished.emit((success, message))
        except Exception as e:
            # Menangkap error apapun dan mengirimkannya sebagai sinyal 'error'.
            self.error.emit(str(e))


# --- Kelas Utama Aplikasi ---
class MaSubsBurnerApp(QMainWindow):
    """
    Kelas utama aplikasi yang bertindak sebagai jendela utama (QMainWindow).
    Mengelola semua widget GUI, koneksi sinyal-slot, dan orkestrasi thread.
    """
    def __init__(self):
        super().__init__()
        
        # Properti untuk menyimpan path file yang dipilih oleh pengguna.
        self.video_path = None
        self.subtitle_path = None
        
        # Panggil metode untuk menginisialisasi dan mengatur semua elemen UI.
        self.init_ui()

    def init_ui(self):
        """Menginisialisasi dan mengatur semua komponen antarmuka pengguna (UI)."""
        self.setWindowTitle("MaSubs Burner")
        # Mengatur ikon aplikasi jika file-nya ada.
        if os.path.exists("logo_burner.ico"):
            self.setWindowIcon(QIcon("logo_burner.ico"))
        self.setGeometry(150, 150, 700, 350)

        # Widget pusat dan layout utama untuk menampung semua elemen lain.
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # --- Bagian UI: Pemilihan File Video ---
        self.btn_select_video = QPushButton("1. Pilih File Video...")
        self.btn_select_video.clicked.connect(self.select_video_file)
        self.layout.addWidget(self.btn_select_video)

        self.lbl_video_path = QLabel("Belum ada file video yang dipilih.")
        self.lbl_video_path.setStyleSheet("font-style: italic; color: grey;")
        self.layout.addWidget(self.lbl_video_path)

        # --- Bagian UI: Pemilihan File Subtitle ---
        self.btn_select_subtitle = QPushButton("2. Pilih File Subtitle (.srt)...")
        self.btn_select_subtitle.clicked.connect(self.select_subtitle_file)
        self.layout.addWidget(self.btn_select_subtitle)

        self.lbl_subtitle_path = QLabel("Belum ada file .srt yang dipilih.")
        self.lbl_subtitle_path.setStyleSheet("font-style: italic; color: grey;")
        self.layout.addWidget(self.lbl_subtitle_path)
        
        # --- Bagian UI: Indikator Progres ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False) # Disembunyikan sampai proses dimulai.
        self.layout.addWidget(self.progress_bar)

        # --- Bagian UI: Tombol Aksi Utama ---
        self.btn_start_burn = QPushButton("3. Mulai Proses & Simpan Video")
        self.btn_start_burn.setStyleSheet("font-size: 16px; padding: 10px; background-color: #E74C3C; color: white;")
        self.btn_start_burn.clicked.connect(self.start_burn_process)
        self.layout.addWidget(self.btn_start_burn)

        # --- Status Bar di bagian bawah jendela ---
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Siap")

    def select_video_file(self):
        """Membuka dialog file untuk memilih file video."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih File Video", "", "Video Files (*.mp4 *.mkv *.avi *.mov)")
        if file_name:
            self.video_path = file_name
            # Menampilkan hanya nama file, bukan path lengkap, agar UI lebih rapi.
            self.lbl_video_path.setText(f"Video: {os.path.basename(file_name)}")
            self.lbl_video_path.setStyleSheet("font-style: normal; color: black;")

    def select_subtitle_file(self):
        """Membuka dialog file untuk memilih file subtitle (.srt)."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih File Subtitle", "", "SRT Files (*.srt)")
        if file_name:
            self.subtitle_path = file_name
            self.lbl_subtitle_path.setText(f"Subtitle: {os.path.basename(file_name)}")
            self.lbl_subtitle_path.setStyleSheet("font-style: normal; color: black;")

    def start_burn_process(self):
        """Metode utama yang dipanggil saat tombol 'Mulai' diklik."""
        # 1. Validasi Input: Pastikan kedua file sudah dipilih oleh pengguna.
        if not self.video_path or not self.subtitle_path:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Harap pilih file video dan file subtitle terlebih dahulu.")
            return

        # 2. Dialog "Simpan Sebagai...": Minta pengguna menentukan lokasi penyimpanan file output.
        video_dir = os.path.dirname(self.video_path)
        video_filename, video_ext = os.path.splitext(os.path.basename(self.video_path))
        # Memberikan saran nama file output yang logis.
        suggested_output_name = f"{video_filename}_hardsub{video_ext}"
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Simpan Video Sebagai...", os.path.join(video_dir, suggested_output_name), "Video Files (*.mp4)")
        
        # Jika pengguna menutup/membatalkan dialog, hentikan proses.
        if not output_path:
            self.statusBar().showMessage("Proses dibatalkan oleh pengguna.")
            return

        # 3. Persiapan UI dan Threading
        self.set_ui_enabled(False) # Nonaktifkan tombol untuk mencegah klik berulang.
        self.progress_bar.setVisible(True)
        # 'setRange(0, 0)' mengubah progress bar ke mode "indeterminate" (sibuk).
        self.progress_bar.setRange(0, 0) 
        self.statusBar().showMessage("Memulai proses encoding video...")

        # 4. Inisialisasi dan jalankan thread untuk tugas burning.
        self.thread = QThread()
        self.worker = Worker(self.video_path, self.subtitle_path, output_path)
        self.worker.moveToThread(self.thread)

        # Hubungkan sinyal dari worker ke slot (metode) di thread utama.
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_process_finished)
        self.worker.error.connect(self.on_process_error)
        
        # Atur pembersihan setelah thread selesai.
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        self.thread.start()

    def on_process_finished(self, result):
        """Slot yang dipanggil oleh sinyal 'finished' dari worker."""
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        
        success, message = result
        if success:
            self.statusBar().showMessage("Proses Selesai!")
            QMessageBox.information(self, "Sukses", message)
        else:
            self.statusBar().showMessage("Terjadi kesalahan.")
            # Menampilkan pesan error detail dari ffmpeg ke pengguna.
            QMessageBox.critical(self, "Error", message)

    def on_process_error(self, error_message):
        """Slot yang dipanggil oleh sinyal 'error' dari worker."""
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Error Kritis!")
        QMessageBox.critical(self, "Error Kritis", f"Terjadi kesalahan yang tidak terduga:\n{error_message}")

    def set_ui_enabled(self, is_enabled):
        """Metode utilitas untuk mengaktifkan/menonaktifkan tombol-tombol UI."""
        self.btn_select_video.setEnabled(is_enabled)
        self.btn_select_subtitle.setEnabled(is_enabled)
        self.btn_start_burn.setEnabled(is_enabled)

# --- Titik Masuk Eksekusi Aplikasi ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MaSubsBurnerApp()
    window.show()
    sys.exit(app.exec())