# main_burner.py (versi 2 - dengan logika lengkap)
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QProgressBar, QStatusBar,
    QFileDialog, QMessageBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, QObject, pyqtSignal

# Impor fungsi inti kita
from burner_logic import burn_subtitles

# --- KELAS PEKERJA (WORKER) UNTUK THREADING ---
# Ini adalah "koki" yang akan bekerja di dapur (thread terpisah)
class Worker(QObject):
    # Sinyal yang akan dikirim: hasil (tuple), error (string), progress (string)
    finished = pyqtSignal(tuple)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, video_path, subtitle_path, output_path):
        super().__init__()
        self.video_path = video_path
        self.subtitle_path = subtitle_path
        self.output_path = output_path

    def run(self):
        """Metode ini akan dijalankan di thread terpisah."""
        try:
            # Panggil fungsi inti dari burner_logic.py
            success, message = burn_subtitles(self.video_path, self.subtitle_path, self.output_path)
            self.finished.emit((success, message))
        except Exception as e:
            self.error.emit(str(e))


class MaSubsBurnerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Variabel untuk menyimpan path file
        self.video_path = None
        self.subtitle_path = None

        self.setWindowTitle("MaSubs Burner")
        if os.path.exists("logo_burner.ico"):
            self.setWindowIcon(QIcon("logo_burner.ico"))
        self.setGeometry(150, 150, 700, 350)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # --- 1. Pemilihan File Video ---
        self.btn_select_video = QPushButton("1. Pilih File Video...")
        self.btn_select_video.clicked.connect(self.select_video_file) # Hubungkan ke metode
        self.layout.addWidget(self.btn_select_video)

        self.lbl_video_path = QLabel("Belum ada file video yang dipilih.")
        self.lbl_video_path.setStyleSheet("font-style: italic; color: grey;")
        self.layout.addWidget(self.lbl_video_path)

        # --- 2. Pemilihan File Subtitle ---
        self.btn_select_subtitle = QPushButton("2. Pilih File Subtitle (.srt)...")
        self.btn_select_subtitle.clicked.connect(self.select_subtitle_file) # Hubungkan ke metode
        self.layout.addWidget(self.btn_select_subtitle)

        self.lbl_subtitle_path = QLabel("Belum ada file .srt yang dipilih.")
        self.lbl_subtitle_path.setStyleSheet("font-style: italic; color: grey;")
        self.layout.addWidget(self.lbl_subtitle_path)
        
        # --- 3. Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        # --- 4. Tombol Aksi Utama ---
        self.btn_start_burn = QPushButton("3. Mulai Proses & Simpan Video")
        self.btn_start_burn.setStyleSheet("font-size: 16px; padding: 10px; background-color: #E74C3C; color: white;")
        self.btn_start_burn.clicked.connect(self.start_burn_process) # Hubungkan ke metode
        self.layout.addWidget(self.btn_start_burn)

        # --- 5. Status Bar ---
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Siap")

    # --- METODE-METODE BARU UNTUK FUNGSI APLIKASI ---

    def select_video_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih File Video", "", "Video Files (*.mp4 *.mkv *.avi *.mov)")
        if file_name:
            self.video_path = file_name
            self.lbl_video_path.setText(f"Video: {os.path.basename(file_name)}")
            self.lbl_video_path.setStyleSheet("font-style: normal; color: black;")

    def select_subtitle_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih File Subtitle", "", "SRT Files (*.srt)")
        if file_name:
            self.subtitle_path = file_name
            self.lbl_subtitle_path.setText(f"Subtitle: {os.path.basename(file_name)}")
            self.lbl_subtitle_path.setStyleSheet("font-style: normal; color: black;")

    def start_burn_process(self):
        # 1. Validasi: Pastikan kedua file sudah dipilih
        if not self.video_path or not self.subtitle_path:
            QMessageBox.warning(self, "Input Tidak Lengkap", "Harap pilih file video dan file subtitle terlebih dahulu.")
            return

        # 2. Dapatkan lokasi & nama file output dari pengguna (dialog "Save As")
        video_dir = os.path.dirname(self.video_path)
        video_filename, video_ext = os.path.splitext(os.path.basename(self.video_path))
        suggested_output_name = f"{video_filename}_hardsub{video_ext}"
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Simpan Video Sebagai...", os.path.join(video_dir, suggested_output_name), "Video Files (*.mp4)")
        
        if not output_path:
            # Pengguna membatalkan dialog "Save As"
            self.statusBar().showMessage("Proses dibatalkan oleh pengguna.")
            return

        # 3. Persiapkan GUI untuk proses
        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) # Mode "sibuk", bar akan bergerak terus
        self.statusBar().showMessage("Mempersiapkan proses...")

        # 4. Siapkan dan jalankan Thread
        self.thread = QThread()
        self.worker = Worker(self.video_path, self.subtitle_path, output_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_process_finished)
        self.worker.error.connect(self.on_process_error)
        
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        self.thread.start()

    def on_process_finished(self, result):
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        
        success, message = result
        if success:
            self.statusBar().showMessage("Proses Selesai!")
            QMessageBox.information(self, "Sukses", message)
        else:
            self.statusBar().showMessage("Terjadi kesalahan.")
            QMessageBox.critical(self, "Error", message)

    def on_process_error(self, error_message):
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Error Kritis!")
        QMessageBox.critical(self, "Error Kritis", f"Terjadi kesalahan yang tidak terduga:\n{error_message}")

    def set_ui_enabled(self, is_enabled):
        """Mengaktifkan/menonaktifkan tombol-tombol."""
        self.btn_select_video.setEnabled(is_enabled)
        self.btn_select_subtitle.setEnabled(is_enabled)
        self.btn_start_burn.setEnabled(is_enabled)

# --- Bagian untuk Menjalankan Aplikasi ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MaSubsBurnerApp()
    window.show()
    sys.exit(app.exec())