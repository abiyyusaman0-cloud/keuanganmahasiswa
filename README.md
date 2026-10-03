# 💰 Keuangan Mahasiswa

Aplikasi web sederhana untuk mengatur dan mengelola keuangan bulanan mahasiswa.
Dibangun dengan **Flask**, **SQLite**, **Jinja2**, dan **Bootstrap 5**.

## 1. Deskripsi Aplikasi

Keuangan Mahasiswa membantu mahasiswa mencatat uang masuk (misalnya kiriman orang tua,
beasiswa, gaji part-time) dan uang keluar (makan, transport, kuliah, dll.), lalu otomatis
menghitung **sisa uang yang dapat ditabung** setiap bulan.

Rumus: `Sisa Uang = Total Pemasukan - Total Pengeluaran`

## 2. Fitur

- **Dashboard**: total pemasukan, total pengeluaran, sisa uang (hijau/biru jika positif,
  merah jika negatif), daftar pengeluaran bulan terpilih, dan filter bulan.
- **Pemasukan**: tambah pemasukan per bulan + riwayat + hapus (dengan konfirmasi).
- **Pengeluaran**: tambah pengeluaran (tanggal, nominal, deskripsi, kategori, sumber dana)
  + riwayat + hapus (POST + konfirmasi).
- **Filter pengeluaran**: berdasarkan bulan, kategori, dan sumber dana (dapat digabung).
- Format Rupiah otomatis (`Rp 3.000.000`).
- Validasi input dan flash message.
- Responsif untuk laptop dan smartphone.

## 3. Struktur Folder

```
keuangan-mahasiswa/
│
├── app.py
├── requirements.txt
├── Procfile
├── README.md
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── pemasukan.html
│   └── pengeluaran.html
│
└── static/
    └── css/
        └── style.css
```

File database `finance.db` dibuat otomatis saat aplikasi pertama kali dijalankan.

## 4. Cara Install Python

1. Unduh Python 3.10 atau lebih baru dari <https://www.python.org/downloads/>.
2. **Windows**: centang opsi **"Add Python to PATH"** saat instalasi.
3. Cek instalasi:
   ```bash
   python --version      # Windows
   python3 --version     # Linux/macOS
   ```

## 5. Cara Membuat Virtual Environment

Masuk ke folder project terlebih dahulu:

```bash
cd keuangan-mahasiswa
```

**Windows**
```bash
python -m venv venv
```

**Linux/macOS**
```bash
python3 -m venv venv
```

## 6. Mengaktifkan Virtual Environment di Windows

```bash
venv\Scripts\activate
```

> Jika di PowerShell muncul error *execution policy*, jalankan:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, atau gunakan Command Prompt (cmd).

## 7. Mengaktifkan Virtual Environment di Linux/macOS

```bash
source venv/bin/activate
```

## 8. Cara Install Requirements

```bash
pip install -r requirements.txt
```

## 9. Cara Menjalankan Aplikasi

```bash
python app.py
```

(Di Linux/macOS dapat menggunakan `python3 app.py` bila `python` tidak tersedia di luar venv.)

## 10. URL Localhost

Buka di browser:

```
http://127.0.0.1:5000
```

Port dapat diubah lewat environment variable `PORT`, misalnya `PORT=8000 python app.py`.

## Menjalankan di VS Code

1. Buka VS Code, pilih **File → Open Folder**, lalu pilih folder `keuangan-mahasiswa`.
2. Buka terminal (**Terminal → New Terminal**).
3. Buat dan aktifkan virtual environment (langkah 5-7), lalu `pip install -r requirements.txt`.
4. Tekan `Ctrl+Shift+P` → **Python: Select Interpreter** → pilih interpreter di folder `venv`.
5. Jalankan `python app.py`, lalu buka `http://127.0.0.1:5000`.

## Cara Testing Fitur

1. **Database otomatis**: setelah `python app.py` dijalankan, file `finance.db` muncul di folder project.
2. **Pemasukan**: buka menu *Pemasukan*, isi Bulan `2026-10`, Nominal `3000000`,
   Keterangan `Uang bulanan dari orang tua` → Simpan. Data muncul di tabel dengan nominal `Rp 3.000.000`.
3. **Pengeluaran**: buka menu *Pengeluaran*, isi Tanggal `2026-10-03`, Nominal `25000`,
   Deskripsi `Makan siang`, Kategori `Makanan`, Sumber Dana `E-Money` → Simpan.
4. **Filter**: tambahkan beberapa transaksi berbeda, lalu filter Bulan `2026-10` + Kategori `Makanan`
   + Sumber Dana `E-Money`. Hanya transaksi yang cocok yang tampil. Klik *Reset* untuk menampilkan semua.
5. **Dashboard**: buka menu *Dashboard*, pilih bulan `2026-10`. Periksa
   Total Pemasukan `Rp 3.000.000`, Total Pengeluaran `Rp 25.000`, Sisa Uang `Rp 2.975.000` (biru).
   Tambahkan pengeluaran lebih besar dari pemasukan, sisa uang berubah merah.
6. **Hapus**: klik *Hapus* pada baris data, muncul konfirmasi "Yakin ingin menghapus data ini?".
   Klik OK, data hilang dan muncul pesan sukses.
7. **Validasi**: kirim nominal `0`, `-5`, atau `abc` (melalui form atau dengan menonaktifkan validasi
   browser), muncul pesan merah yang menjelaskan kesalahan.

## 11. Deployment ke Render.com

1. **Buat repository GitHub**: buka <https://github.com/new>, buat repository baru
   (misalnya `keuangan-mahasiswa`).
2. **Upload project**:
   ```bash
   git init
   git add .
   git commit -m "Versi pertama Keuangan Mahasiswa"
   git branch -M main
   git remote add origin https://github.com/USERNAME/keuangan-mahasiswa.git
   git push -u origin main
   ```
3. **Buat Web Service**: login ke <https://render.com>, klik **New + → Web Service**.
4. **Hubungkan repository**: pilih repository GitHub `keuangan-mahasiswa`.
5. **Build Command**:
   ```
   pip install -r requirements.txt
   ```
6. **Start Command**:
   ```
   gunicorn app:app
   ```
7. **Environment variable**: pada bagian *Environment*, tambahkan `SECRET_KEY` dengan nilai acak
   yang panjang (lihat bagian "Cara Mengatur SECRET_KEY").
8. Klik **Create Web Service** dan tunggu proses deploy selesai. URL aplikasi tampil di bagian atas halaman service.

> **Catatan penting:** SQLite menyimpan data di file lokal. Pada paket gratis Render, filesystem
> bersifat sementara sehingga **data dapat hilang** saat service di-restart atau di-deploy ulang.
> Untuk penggunaan jangka panjang, gunakan database **PostgreSQL** atau tambahkan
> **persistent disk** (lalu arahkan `DATABASE_PATH` ke lokasi disk tersebut, misalnya `/data/finance.db`).

## 12. Deployment ke PythonAnywhere

1. **Buat akun**: daftar akun gratis (Beginner) di <https://www.pythonanywhere.com>.
2. **Upload project**: buka tab **Files** lalu upload folder project (atau buka konsol **Bash** dan
   jalankan `git clone https://github.com/USERNAME/keuangan-mahasiswa.git`).
3. **Buat virtual environment** (di konsol Bash):
   ```bash
   cd ~/keuangan-mahasiswa
   python3 -m venv venv
   source venv/bin/activate
   ```
4. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Buat Web App**: tab **Web → Add a new web app → Manual configuration**, pilih versi Python
   yang sama dengan yang dipakai untuk membuat venv.
6. **Atur Virtualenv**: pada bagian *Virtualenv* isi `/home/USERNAME/keuangan-mahasiswa/venv`.
   Pada bagian *Source code* isi `/home/USERNAME/keuangan-mahasiswa`.
7. **Atur WSGI**: klik link file WSGI configuration, hapus isinya lalu ganti dengan:
   ```python
   import sys

   path = "/home/USERNAME/keuangan-mahasiswa"
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```
   Ganti `USERNAME` dengan username PythonAnywhere kamu.
8. **Reload Web App**: klik tombol hijau **Reload** di tab Web.
9. **Buka aplikasi**: akses `https://USERNAME.pythonanywhere.com`.

Di PythonAnywhere file SQLite tersimpan permanen di disk akun, sehingga lebih cocok untuk SQLite
dibanding paket gratis Render.

## 13. Cara Mengatur SECRET_KEY

`SECRET_KEY` dipakai Flask untuk mengamankan session dan flash message. Jika tidak diatur,
aplikasi memakai nilai bawaan `development-secret-key` (hanya untuk pengembangan lokal).

Buat nilai acak:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Lalu atur:

- **Windows (cmd)**: `set SECRET_KEY=nilai-acak-anda`
- **Windows (PowerShell)**: `$env:SECRET_KEY="nilai-acak-anda"`
- **Linux/macOS**: `export SECRET_KEY="nilai-acak-anda"`
- **Render.com**: tab *Environment* → *Add Environment Variable*.
- **PythonAnywhere**: tambahkan di file WSGI sebelum `from app import app as application`:
  ```python
  import os
  os.environ["SECRET_KEY"] = "nilai-acak-anda"
  ```

## 14. Catatan tentang SQLite pada Hosting

- SQLite adalah file (`finance.db`) di server, bukan server database terpisah.
- Hosting dengan filesystem sementara (misalnya Render paket gratis, Heroku) akan menghapus
  file tersebut saat restart/redeploy. Gunakan persistent disk atau database eksternal seperti PostgreSQL.
- Aplikasi ini cocok untuk pemakaian pribadi atau pengguna sedikit. Untuk banyak pengguna
  bersamaan, pertimbangkan PostgreSQL.
- Lakukan backup berkala dengan menyalin `finance.db`.
- Aplikasi ini belum memiliki fitur login, jadi siapa pun yang tahu URL dapat melihat dan mengubah
  data. Jangan publikasikan data keuangan pribadi tanpa menambahkan autentikasi.
- File `finance.db` sudah dimasukkan ke `.gitignore` agar tidak ikut ter-upload ke GitHub.

## Lisensi

Bebas dipakai dan dimodifikasi untuk keperluan belajar.
