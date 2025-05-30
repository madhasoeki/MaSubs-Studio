# main_app.py (versi final dengan ffmpeg terbundel)
import sys
import os

# --- BLOK KODE UNTUK MEMBUNDEL FFMPEG ---
# Cek apakah aplikasi berjalan sebagai .exe dari PyInstaller
if getattr(sys, 'frozen', False):
    # Jika ya, dapatkan path ke direktori sementara _MEIPASS
    application_path = sys._MEIPASS
    # Tambahkan path ini ke awal dari environment variable PATH
    # Ini akan membuat pustaka 'whisper' mencari ffmpeg di sini terlebih dahulu
    os.environ['PATH'] = application_path + os.pathsep + os.environ.get('PATH', '')
# --- AKHIR BLOK KODE ---

# Sisa impor Anda tetap di sini
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit, QStatusBar,
    QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from PyQt6.QtGui import QIcon
from core_logic import transcribe_audio, AVAILABLE_MODELS

# ... dan sisa seluruh kode kelas Worker dan MaSubsApp Anda ...
# Tidak ada perubahan lain di sisa file ini, hanya penambahan blok di atas.
# Pastikan Anda meletakkan blok kode tersebut di bagian paling atas setelah 'import sys' dan 'import os'.

class Worker(QObject):
    finished = pyqtSignal(tuple)
    error = pyqtSignal(str)
    # PERUBAHAN: Sinyal progress sekarang mengirimkan integer (persen) dan string (pesan)
    progress = pyqtSignal(int, str)

    def __init__(self, file_path, model_name):
        super().__init__()
        self.file_path = file_path
        self.model_name = model_name

    def run(self):
        try:
            # PERUBAHAN: Kita lewatkan sinyal progress dari worker ke fungsi inti
            result_tuple = transcribe_audio(self.file_path, self.model_name, self.progress)
            self.finished.emit(result_tuple)
        except Exception as e:
            self.error.emit(str(e))

class MaSubsApp(QMainWindow): # Ganti nama kelas menjadi MaSubsApp
    def __init__(self):
        super().__init__()
        self.selected_file_path = None
        
        # --- PENGATURAN NAMA, UKURAN, DAN LOGO APLIKASI ---
        self.setWindowTitle("MaSubs - Auto Subtitle Generator")
        if os.path.exists("logo.ico"):
            self.setWindowIcon(QIcon("logo.ico"))
        self.setGeometry(100, 100, 700, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # ... (Widget tombol, label, dll tetap sama) ...
        self.btn_browse = QPushButton("1. Pilih File Audio/Video...")
        self.btn_browse.clicked.connect(self.open_file_dialog)
        self.layout.addWidget(self.btn_browse)

        self.lbl_file_path = QLabel("Belum ada file yang dipilih.")
        self.lbl_file_path.setStyleSheet("font-style: italic; color: grey;")
        self.layout.addWidget(self.lbl_file_path)

        self.lbl_model = QLabel("2. Pilih Model Transkripsi:")
        self.layout.addWidget(self.lbl_model)

        self.combo_model = QComboBox()
        self.combo_model.addItems(AVAILABLE_MODELS)
        self.combo_model.setCurrentText("base")
        self.layout.addWidget(self.combo_model)

        # --- MENGGANTI LOADING GIF DENGAN PROGRESS BAR ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False) # Sembunyikan pada awalnya
        self.layout.addWidget(self.progress_bar)
        
        self.btn_start = QPushButton("3. Mulai Transkripsi")
        self.btn_start.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")
        self.btn_start.clicked.connect(self.start_transcription)
        self.layout.addWidget(self.btn_start)

        self.lbl_result = QLabel("Hasil Transkripsi:")
        self.layout.addWidget(self.lbl_result)

        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        self.layout.addWidget(self.text_result)

        self.setStatusBar(QStatusBar(self))
        self.update_status("Siap")
        
    def start_transcription(self):
        if not self.selected_file_path:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih file terlebih dahulu!")
            return

        self.btn_start.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.text_result.clear()
        self.progress_bar.setVisible(True) # Tampilkan progress bar
        self.progress_bar.setValue(0)

        selected_model = self.combo_model.currentText()
        
        self.thread = QThread()
        self.worker = Worker(self.selected_file_path, selected_model)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_transcription_finished)
        self.worker.error.connect(self.on_transcription_error)
        # PERUBAHAN: Hubungkan sinyal progress yang baru ke slot update_progress
        self.worker.progress.connect(self.update_progress)

        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        self.thread.start()

    # SLOT BARU untuk menangani sinyal progress
    def update_progress(self, percent, message):
        self.progress_bar.setValue(percent)
        self.update_status(message)

    def on_transcription_finished(self, result_tuple):
        self.progress_bar.setValue(100)
        self.update_status("Transkripsi Selesai!")

        plain_text, saved_path = result_tuple
        self.text_result.setText(plain_text)
        
        QMessageBox.information(self, "Sukses", f"Proses transkripsi telah selesai!\n\nFile subtitle disimpan di:\n{saved_path}")
        
        self.btn_start.setEnabled(True)
        self.btn_browse.setEnabled(True)
        self.progress_bar.setVisible(False)

    def on_transcription_error(self, error_message):
        self.progress_bar.setVisible(False)
        self.update_status(f"Error!")
        QMessageBox.critical(self, "Error", f"Terjadi kesalahan:\n{error_message}")
        self.btn_start.setEnabled(True)
        self.btn_browse.setEnabled(True)

    def open_file_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih File Audio/Video", "", "All Files (*);;Audio Files (*.mp3 *.wav *.m4a);;Video Files (*.mp4 *.mkv)")
        if file_name:
            self.selected_file_path = file_name
            self.lbl_file_path.setText(f"File: {file_name}")
            self.lbl_file_path.setStyleSheet("font-style: normal; color: black;")
            self.update_status(f"File dipilih: {file_name}")
            
    def update_status(self, message):
        self.statusBar().showMessage(message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MaSubsApp() # Ganti nama kelas menjadi MaSubsApp
    window.show()
    sys.exit(app.exec())