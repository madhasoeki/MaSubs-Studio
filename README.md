# MaSubs Studio

Selamat datang di MaSubs Studio! Ini adalah sebuah _suite_ yang terdiri dari dua aplikasi Windows untuk membantu Anda dalam membuat dan menambahkan subtitle ke video Anda secara otomatis.

## Daftar Isi
1.  [Penjelasan Aplikasi](#1-penjelasan-aplikasi)
    * [MaSubs (Transcriber Otomatis)](#masubs-transcriber-otomatis)
    * [MaSubsBurner (Hardcode Subtitle)](#masubsburner-hardcode-subtitle)
2.  [Teknologi & Model Whisper](#2-teknologi--model-whisper)
    * [Model yang Tersedia dan Spesifikasinya](#model-yang-tersedia-dan-spesifikasinya)
3.  [Saran Aplikasi Pendukung](#3-saran-aplikasi-pendukung)
4.  [Cara Mengunduh & Instalasi](#4-cara-mengunduh--instalasi)
5.  [Cara Penggunaan](#5-cara-penggunaan)
    * [Menggunakan MaSubs](#menggunakan-masubs)
    * [Menggunakan MaSubsBurner](#menggunakan-masubsburner)
    * [Mengedit Subtitle dengan Subtitle Edit](#mengedit-subtitle-dengan-subtitle-edit)
    * [Menggunakan Video di Kdenlive/Shotcut](#menggunakan-video-di-kdenliveshotcut)
6.  [Untuk Pengembang (Menjalankan dari Kode Sumber)](#6-untuk-pengembang-menjalankan-dari-kode-sumber)

---

## 1. Penjelasan Aplikasi

MaSubs Studio terdiri dari dua aplikasi utama:

### MaSubs (Transcriber Otomatis)
`MaSubs` adalah aplikasi yang dirancang untuk mentranskripsi file audio atau video menjadi teks secara otomatis dan menghasilkan file subtitle dalam format `.srt` lengkap dengan _timestamp_. Aplikasi ini memanfaatkan kecanggihan model _Artificial Intelligence_ (AI) **OpenAI Whisper** untuk akurasi transkripsi yang tinggi.

**Fitur Utama MaSubs:**
* Transkripsi otomatis dari berbagai format file audio dan video.
* Pemilihan model Whisper (dari `tiny` hingga `large`) untuk keseimbangan antara kecepatan dan akurasi.
* Output berupa teks transkripsi dan file `.srt` yang siap digunakan.
* Antarmuka pengguna grafis (GUI) yang mudah digunakan.

### MaSubsBurner (Hardcode Subtitle)
`MaSubsBurner` adalah aplikasi pendamping yang berfungsi untuk "membakar" atau melakukan _hardcode_ file subtitle (`.srt`) yang sudah ada ke dalam file video Anda. Hasilnya adalah sebuah file video baru di mana teks subtitle sudah menjadi bagian permanen dari gambar video.

**Fitur Utama MaSubsBurner:**
* Menggabungkan file `.srt` dengan berbagai format video populer.
* Proses _hardcoding_ yang memastikan subtitle tampil di semua pemutar video.
* Antarmuka pengguna grafis (GUI) yang sederhana dan _to-the-point_.

---

## 2. Teknologi & Model Whisper

Kedua aplikasi ini dibangun menggunakan **Python** dengan antarmuka pengguna grafis (GUI) yang dibuat menggunakan **PyQt6**. Proses transkripsi pada `MaSubs` ditenagai oleh **OpenAI Whisper**, sebuah model pengenalan suara otomatis (_Automatic Speech Recognition_ - ASR) yang canggih. Proses manipulasi video pada `MaSubsBurner` dan pemrosesan audio pada `MaSubs` difasilitasi oleh **FFmpeg** yang sudah dibundel di dalam aplikasi.

### Model Whisper yang Tersedia dan Spesifikasinya
MaSubs memungkinkan Anda memilih berbagai ukuran model Whisper. Pilihan model mempengaruhi kecepatan transkripsi, akurasi, dan kebutuhan sumber daya sistem (terutama VRAM jika menggunakan GPU).

| Model   | Kecepatan Relatif | Akurasi Relatif | Estimasi VRAM (GPU) | Catatan                                                                 |
| :------ | :---------------- | :-------------- | :------------------ | :-------------------------------------------------------------------- |
| `tiny`  | Sangat Cepat      | Cukup           | ~1 GB               | Paling ringan, cocok untuk transkripsi cepat atau perangkat terbatas.   |
| `base`  | Cepat             | Baik            | ~1 GB               | Keseimbangan baik antara kecepatan dan akurasi untuk penggunaan umum. |
| `small` | Sedang            | Sangat Baik     | ~2 GB               | Akurasi lebih tinggi, membutuhkan sumber daya lebih.                   |
| `medium`| Lambat            | Luar Biasa      | ~5 GB               | Akurasi sangat tinggi, cocok untuk audio berkualitas tinggi atau kompleks. |
| `large` | Sangat Lambat     | Terbaik         | ~10 GB              | Model paling akurat dan paling berat.                                   |

**Catatan Penting:**
* **Pemrosesan CPU:** Semua model dapat dijalankan menggunakan CPU saja, namun prosesnya akan **jauh lebih lambat** dibandingkan menggunakan GPU (kartu grafis) yang kompatibel (NVIDIA dengan CUDA).
* **Unduhan Model:** Saat Anda pertama kali memilih dan menggunakan sebuah model di `MaSubs`, aplikasi akan mengunduh file model tersebut dari internet. Ini hanya terjadi sekali per model. Pastikan ada koneksi internet saat penggunaan pertama.

---

## 3. Saran Aplikasi Pendukung

Meskipun MaSubs Studio menyediakan fungsionalitas inti, Anda mungkin memerlukan alat bantu lain untuk alur kerja yang lebih lengkap:

* **[Subtitle Edit](https://www.nikse.dk/subtitleedit/)**:
    * Gratis dan _open-source_.
    * Sangat direkomendasikan untuk mengedit file `.srt` yang dihasilkan oleh `MaSubs`. Anda bisa memperbaiki kesalahan transkripsi, menyesuaikan _timing_, memformat teks, dll.
    * [Unduh Subtitle Edit](https://github.com/SubtitleEdit/subtitleedit/releases)

* **[Kdenlive](https://kdenlive.org/en/)** atau **[Shotcut](https://shotcut.org/)**:
    * Keduanya adalah editor video gratis, _open-source_, dan _cross-platform_.
    * Berguna jika Anda perlu melakukan editing video lebih lanjut, seperti memotong klip, menambahkan efek, atau jika Anda lebih suka menggunakan _soft subtitles_ (subtitle yang bisa diaktifkan/nonaktifkan oleh pemirsa) dengan mengimpor file `.srt` secara terpisah.
    * [Unduh Kdenlive](https://kdenlive.org/en/download/)
    * [Unduh Shotcut](https://shotcut.org/download/)

---

## 4. Cara Mengunduh & Instalasi

Aplikasi MaSubs dan MaSubsBurner disediakan sebagai file `.exe` yang portabel dan **sudah menyertakan `ffmpeg.exe` di dalamnya**. Anda tidak perlu menginstal dependensi tambahan apa pun untuk menjalankannya.

1.  **Unduh Aplikasi:**
    * Kunjungi halaman **[Releases](PAUTAN_KE_HALAMAN_RELEASES_GITHUB_ANDA)** di repositori GitHub ini.
    * Unduh file `MaSubs.exe` dan/atau `MaSubsBurner.exe` dari rilis terbaru.
2.  **Jalankan Aplikasi:**
    * Setelah diunduh, Anda bisa langsung menjalankan file `.exe` tersebut. Tidak ada proses instalasi formal yang diperlukan. Simpan file `.exe` di lokasi yang mudah Anda akses.

**PENTING:** Ganti `PAUTAN_KE_HALAMAN_RELEASES_GITHUB_ANDA` di atas dengan pautan sebenarnya ke halaman _Releases_ proyek Anda setelah Anda membuatnya di GitHub.

---

## 5. Cara Penggunaan

### Menggunakan MaSubs
1.  Jalankan `MaSubs.exe`.
2.  Klik tombol **"1. Pilih File Audio/Video..."** untuk memilih file yang ingin Anda transkripsi.
3.  Pada bagian **"2. Pilih Model Transkripsi:"**, pilih model Whisper yang Anda inginkan dari menu _dropdown_. Pertimbangkan keseimbangan antara kecepatan dan akurasi (lihat [tabel model](#model-yang-tersedia-dan-spesifikasinya)).
4.  Klik tombol besar **"3. Mulai Transkripsi"**.
5.  Tunggu proses selesai. _Progress bar_ akan menunjukkan kemajuan, dan status bar akan memberikan informasi. Aplikasi akan tetap responsif selama proses.
6.  Setelah selesai, teks hasil transkripsi akan muncul di area teks.
7.  Sebuah file subtitle dengan format `.srt` (misalnya, `nama_video_asli.srt`) akan **otomatis disimpan di folder yang sama** dengan file video/audio sumber Anda.

### Menggunakan MaSubsBurner
1.  Jalankan `MaSubsBurner.exe`.
2.  Klik tombol **"1. Pilih File Video..."** untuk memilih file video yang ingin Anda tambahkan subtitle permanen.
3.  Klik tombol **"2. Pilih File Subtitle (.srt)..."** untuk memilih file `.srt` yang sesuai (bisa hasil dari `MaSubs` atau dari sumber lain).
4.  Klik tombol **"3. Mulai Proses & Simpan Video"**.
5.  Sebuah jendela dialog "Simpan Video Sebagai..." akan muncul.
    * Secara _default_, dialog ini akan terbuka di folder yang sama dengan video input Anda.
    * Nama file output juga akan disarankan secara otomatis (misalnya, `nama_video_asli_hardsub.mp4`).
    * Anda bisa memilih lokasi penyimpanan dan nama file yang berbeda jika diinginkan. Klik "Simpan".
6.  Tunggu proses _burning_ selesai. _Progress bar_ akan aktif.
7.  Setelah selesai, sebuah pesan sukses akan muncul, dan file video baru dengan subtitle yang sudah menempel permanen akan tersedia di lokasi yang Anda pilih.

### Mengedit Subtitle dengan Subtitle Edit
1.  Buka aplikasi **Subtitle Edit**.
2.  Pilih menu `File > Open` (atau seret file `.srt` ke jendela aplikasi).
3.  Buka file `.srt` yang dihasilkan oleh `MaSubs`.
4.  Anda sekarang bisa:
    * Memperbaiki kesalahan ketik atau tata bahasa pada teks subtitle.
    * Menyesuaikan waktu (_timing_) mulai dan selesai untuk setiap baris subtitle agar sinkron dengan audio.
    * Menggabungkan atau memecah baris subtitle.
    * Menggunakan berbagai alat bantu lain yang disediakan Subtitle Edit.
5.  Setelah selesai mengedit, simpan perubahan Anda (`File > Save`). File `.srt` yang sudah diedit ini siap digunakan oleh `MaSubsBurner` atau diimpor ke editor video.

### Menggunakan Video di Kdenlive/Shotcut

* **Untuk Video yang Sudah di-Hardcode oleh MaSubsBurner:**
    1.  Buka Kdenlive atau Shotcut.
    2.  Impor file video yang sudah memiliki subtitle permanen (hasil dari `MaSubsBurner`) ke dalam proyek Anda.
    3.  Subtitle sudah menjadi bagian dari video dan akan selalu tampil. Anda bisa melanjutkan proses editing video lainnya.

* **Untuk Soft Subtitles (Menggunakan File `.srt` Terpisah):**
    1.  Buka Kdenlive atau Shotcut.
    2.  Impor file video **asli** (tanpa subtitle) ke dalam proyek Anda.
    3.  Cari fitur untuk menambahkan _track subtitle_ atau mengimpor file subtitle.
        * **Di Kdenlive:** Anda bisa menambahkan _track_ baru, lalu klik kanan pada _track_ tersebut dan pilih "Add Subtitle File" atau sejenisnya.
        * **Di Shotcut:** Anda mungkin perlu menggunakan filter "Text: SubRip" atau "Text: Rich" dan mengimpor konten dari file `.srt`.
    4.  Arahkan ke file `.srt` yang Anda miliki (bisa dari `MaSubs` atau yang sudah diedit).
    5.  Subtitle akan muncul sebagai _track_ terpisah, memungkinkan pemirsa untuk mengaktifkan atau menonaktifkannya jika format output video mendukungnya.

---

## 6. Untuk Pengembang (Menjalankan dari Kode Sumber)

Jika Anda ingin menjalankan aplikasi dari kode sumber (`.py`):

1.  **Persyaratan:**
    * Python (disarankan versi 3.9+)
    * `pip` (biasanya sudah terinstal bersama Python)
2.  **Clone Repositori:**
    ```bash
    git clone PAUTAN_KE_REPOSITORI_GITHUB_ANDA
    cd NAMA_REPOSITORI_ANDA
    ```
3.  **Untuk MaSubs:**
    * Masuk ke folder `MaSubs`: `cd MaSubs`
    * Buat dan aktifkan _virtual environment_:
        ```bash
        python -m venv venv
        venv\Scripts\activate  # Untuk Windows
        # source venv/bin/activate  # Untuk macOS/Linux
        ```
    * Instal dependensi:
        ```bash
        pip install openai-whisper PyQt6
        ```
    * (Opsional untuk _bundling_ jika menjalankan build dari source) Letakkan `ffmpeg.exe` dan `ffprobe.exe` di folder `MaSubs`.
    * Jalankan: `python main_app.py`
4.  **Untuk MaSubsBurner:**
    * Masuk ke folder `MaSubsBurner`: `cd MaSubsBurner` (dari _root_ repositori)
    * Buat dan aktifkan _virtual environment_:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
    * Instal dependensi:
        ```bash
        pip install ffmpeg-python PyQt6
        ```
    * (Opsional untuk _bundling_ jika menjalankan build dari source) Letakkan `ffmpeg.exe` dan `ffprobe.exe` di folder `MaSubsBurner`.
    * Jalankan: `python main_burner.py`

**Struktur Proyek (Jika Anda Mengunduh Seluruh Kode Sumber):**

MaSubs-Studio/ (Folder Root Repositori Anda)
├── MaSubs/                     # Aplikasi untuk transkripsi otomatis
│   ├── core_logic.py
│   ├── main_app.py
│   ├── main_app.spec         # (Digunakan PyInstaller untuk build .exe, jika disertakan)
│   ├── logo.ico
│   ├── ffmpeg.exe            # (Untuk bundling jika menjalankan build dari source)
│   └── ffprobe.exe           # (Untuk bundling jika menjalankan build dari source)
├── MaSubsBurner/               # Aplikasi untuk hardcode subtitle
│   ├── burner_logic.py
│   ├── main_burner.py
│   ├── main_burner.spec      # (Digunakan PyInstaller untuk build .exe, jika disertakan)
│   ├── logo_burner.ico       # (Opsional)
│   ├── ffmpeg.exe            # (Untuk bundling jika menjalankan build dari source)
│   └── ffprobe.exe           # (Untuk bundling jika menjalankan build dari source)
└── README.md


**Saran `.gitignore` (Jika Anda Mengelola Kode Sumber):**

Virtual Environments
venv/
*/venv/

PyInstaller - Direktori output build dan .exe
build/
*/build/
dist/
*/dist/

*.spec # Komentari jika Anda ingin menyertakan file .spec yang sudah dikustomisasi
Python cache
pycache/
*.py[cod]

IDE/Editor specific
.vscode/
.idea/
*.swp


---

Semoga MaSubs Studio bermanfaat! Jika ada pertanyaan atau masukan, jangan ragu untuk membuka _Issue_.
