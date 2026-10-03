"""Keuangan Mahasiswa - aplikasi pengelola keuangan bulanan mahasiswa.

Backend : Flask + SQLite (sqlite3 bawaan Python)
Frontend: Jinja2 + Bootstrap 5 (CDN)
"""

import math
import os
import re
import sqlite3
from datetime import date, datetime

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "finance.db"))
SECRET_KEY = os.environ.get("SECRET_KEY", "development-secret-key")

KATEGORI_LIST = [
    "Makanan",
    "Transportasi",
    "Kuliah",
    "Hiburan",
    "Belanja",
    "Tagihan",
    "Kesehatan",
    "Lainnya",
]
SUMBER_DANA_LIST = ["Rekening Bank", "E-Money"]

# Warna badge Bootstrap untuk tiap kategori
KATEGORI_WARNA = {
    "Makanan": "warning text-dark",
    "Transportasi": "info text-dark",
    "Kuliah": "primary",
    "Hiburan": "danger",
    "Belanja": "success",
    "Tagihan": "secondary",
    "Kesehatan": "dark",
    "Lainnya": "light text-dark border",
}
SUMBER_DANA_WARNA = {
    "Rekening Bank": "primary",
    "E-Money": "success",
}

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def get_db():
    """Ambil koneksi SQLite untuk request yang sedang berjalan."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Buat tabel jika belum ada (database dibuat otomatis oleh SQLite)."""
    db = sqlite3.connect(DATABASE)
    try:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS pemasukan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bulan TEXT NOT NULL,
                nominal REAL NOT NULL,
                keterangan TEXT
            );

            CREATE TABLE IF NOT EXISTS pengeluaran (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT NOT NULL,
                nominal REAL NOT NULL,
                deskripsi TEXT NOT NULL,
                kategori TEXT NOT NULL,
                sumber_dana TEXT NOT NULL
            );
            """
        )
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Helper: format & validasi
# ---------------------------------------------------------------------------
@app.template_filter("rupiah")
def format_rupiah(value):
    """3000000 -> 'Rp 3.000.000' (nilai negatif -> '-Rp 1.000')."""
    try:
        angka = int(round(float(value or 0)))
    except (TypeError, ValueError):
        angka = 0
    teks = f"{abs(angka):,}".replace(",", ".")
    return f"-Rp {teks}" if angka < 0 else f"Rp {teks}"


@app.template_filter("tanggal_id")
def format_tanggal(value):
    """2026-10-03 -> '03 Okt 2026'."""
    nama_bulan = [
        "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
        "Jul", "Agu", "Sep", "Okt", "Nov", "Des",
    ]
    try:
        d = datetime.strptime(value, "%Y-%m-%d")
        return f"{d.day:02d} {nama_bulan[d.month - 1]} {d.year}"
    except (TypeError, ValueError):
        return value


@app.template_filter("bulan_id")
def format_bulan(value):
    """2026-10 -> 'Oktober 2026'."""
    nama_bulan = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember",
    ]
    try:
        d = datetime.strptime(value, "%Y-%m")
        return f"{nama_bulan[d.month - 1]} {d.year}"
    except (TypeError, ValueError):
        return value


def parse_nominal(raw):
    """Ubah input nominal menjadi float. Return (nilai, pesan_error)."""
    raw = (raw or "").strip()
    if not raw:
        return None, "Nominal wajib diisi."
    try:
        nilai = float(raw)
    except ValueError:
        return None, "Nominal harus berupa angka."
    if math.isnan(nilai) or math.isinf(nilai):
        return None, "Nominal harus berupa angka."
    if nilai <= 0:
        return None, "Nominal harus lebih besar dari 0."
    return nilai, None


def valid_bulan(teks):
    if not teks or not re.fullmatch(r"\d{4}-\d{2}", teks):
        return False
    try:
        datetime.strptime(teks, "%Y-%m")
        return True
    except ValueError:
        return False


def valid_tanggal(teks):
    if not teks:
        return False
    try:
        datetime.strptime(teks, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def bulan_ini():
    return date.today().strftime("%Y-%m")


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------
@app.route("/")
def dashboard():
    bulan = request.args.get("bulan", "").strip()
    if not valid_bulan(bulan):
        if bulan:
            flash("Format bulan tidak valid. Menampilkan bulan ini.", "warning")
        bulan = bulan_ini()

    db = get_db()
    total_pemasukan = db.execute(
        "SELECT COALESCE(SUM(nominal), 0) FROM pemasukan WHERE bulan = ?",
        (bulan,),
    ).fetchone()[0]
    total_pengeluaran = db.execute(
        "SELECT COALESCE(SUM(nominal), 0) FROM pengeluaran "
        "WHERE substr(tanggal, 1, 7) = ?",
        (bulan,),
    ).fetchone()[0]
    daftar_pengeluaran = db.execute(
        "SELECT * FROM pengeluaran WHERE substr(tanggal, 1, 7) = ? "
        "ORDER BY tanggal DESC, id DESC",
        (bulan,),
    ).fetchall()

    sisa_uang = total_pemasukan - total_pengeluaran

    return render_template(
        "dashboard.html",
        bulan=bulan,
        total_pemasukan=total_pemasukan,
        total_pengeluaran=total_pengeluaran,
        sisa_uang=sisa_uang,
        daftar_pengeluaran=daftar_pengeluaran,
        kategori_warna=KATEGORI_WARNA,
        sumber_dana_warna=SUMBER_DANA_WARNA,
    )


@app.route("/pemasukan", methods=["GET", "POST"])
def pemasukan():
    db = get_db()

    if request.method == "POST":
        bulan = request.form.get("bulan", "").strip()
        keterangan = request.form.get("keterangan", "").strip()
        nominal, error_nominal = parse_nominal(request.form.get("nominal"))

        valid = True
        if not valid_bulan(bulan):
            flash("Bulan wajib diisi dengan format yang benar.", "danger")
            valid = False
        if error_nominal:
            flash(error_nominal, "danger")
            valid = False
        if not keterangan:
            flash("Keterangan wajib diisi.", "danger")
            valid = False

        if valid:
            db.execute(
                "INSERT INTO pemasukan (bulan, nominal, keterangan) VALUES (?, ?, ?)",
                (bulan, nominal, keterangan),
            )
            db.commit()
            flash("Data pemasukan berhasil ditambahkan.", "success")
        return redirect(url_for("pemasukan"))

    riwayat = db.execute(
        "SELECT * FROM pemasukan ORDER BY bulan DESC, id DESC"
    ).fetchall()
    return render_template(
        "pemasukan.html", riwayat=riwayat, bulan_default=bulan_ini()
    )


@app.route("/pemasukan/hapus/<int:id>", methods=["POST"])
def hapus_pemasukan(id):
    db = get_db()
    cur = db.execute("DELETE FROM pemasukan WHERE id = ?", (id,))
    db.commit()
    if cur.rowcount:
        flash("Data pemasukan berhasil dihapus.", "success")
    else:
        flash("Data pemasukan tidak ditemukan.", "warning")
    return redirect(url_for("pemasukan"))


@app.route("/pengeluaran", methods=["GET", "POST"])
def pengeluaran():
    db = get_db()

    if request.method == "POST":
        tanggal = request.form.get("tanggal", "").strip()
        deskripsi = request.form.get("deskripsi", "").strip()
        kategori = request.form.get("kategori", "").strip()
        sumber_dana = request.form.get("sumber_dana", "").strip()
        nominal, error_nominal = parse_nominal(request.form.get("nominal"))

        valid = True
        if not valid_tanggal(tanggal):
            flash("Tanggal wajib diisi dengan format yang benar.", "danger")
            valid = False
        if error_nominal:
            flash(error_nominal, "danger")
            valid = False
        if not deskripsi:
            flash("Deskripsi wajib diisi.", "danger")
            valid = False
        if kategori not in KATEGORI_LIST:
            flash("Kategori tidak valid.", "danger")
            valid = False
        if sumber_dana not in SUMBER_DANA_LIST:
            flash("Sumber dana tidak valid.", "danger")
            valid = False

        if valid:
            db.execute(
                "INSERT INTO pengeluaran "
                "(tanggal, nominal, deskripsi, kategori, sumber_dana) "
                "VALUES (?, ?, ?, ?, ?)",
                (tanggal, nominal, deskripsi, kategori, sumber_dana),
            )
            db.commit()
            flash("Data pengeluaran berhasil ditambahkan.", "success")
        return redirect(url_for("pengeluaran"))

    # --- Filter (GET) -------------------------------------------------------
    f_bulan = request.args.get("bulan", "").strip()
    f_kategori = request.args.get("kategori", "").strip()
    f_sumber = request.args.get("sumber_dana", "").strip()

    # Nilai filter yang tidak valid diabaikan (dianggap kosong)
    if f_bulan and not valid_bulan(f_bulan):
        flash("Format filter bulan tidak valid.", "warning")
        f_bulan = ""
    if f_kategori and f_kategori not in KATEGORI_LIST:
        f_kategori = ""
    if f_sumber and f_sumber not in SUMBER_DANA_LIST:
        f_sumber = ""

    # Klausa WHERE disusun dari string tetap; nilai input selalu lewat parameter.
    kondisi = []
    params = []
    if f_bulan:
        kondisi.append("substr(tanggal, 1, 7) = ?")
        params.append(f_bulan)
    if f_kategori:
        kondisi.append("kategori = ?")
        params.append(f_kategori)
    if f_sumber:
        kondisi.append("sumber_dana = ?")
        params.append(f_sumber)

    where = (" WHERE " + " AND ".join(kondisi)) if kondisi else ""
    riwayat = db.execute(
        "SELECT * FROM pengeluaran" + where + " ORDER BY tanggal DESC, id DESC",
        params,
    ).fetchall()
    total_filter = sum(r["nominal"] for r in riwayat)

    return render_template(
        "pengeluaran.html",
        riwayat=riwayat,
        total_filter=total_filter,
        kategori_list=KATEGORI_LIST,
        sumber_dana_list=SUMBER_DANA_LIST,
        kategori_warna=KATEGORI_WARNA,
        sumber_dana_warna=SUMBER_DANA_WARNA,
        f_bulan=f_bulan,
        f_kategori=f_kategori,
        f_sumber=f_sumber,
        filter_aktif=bool(kondisi),
        tanggal_default=date.today().isoformat(),
    )


@app.route("/pengeluaran/hapus/<int:id>", methods=["POST"])
def hapus_pengeluaran(id):
    db = get_db()
    cur = db.execute("DELETE FROM pengeluaran WHERE id = ?", (id,))
    db.commit()
    if cur.rowcount:
        flash("Data pengeluaran berhasil dihapus.", "success")
    else:
        flash("Data pengeluaran tidak ditemukan.", "warning")
    return redirect(url_for("pengeluaran"))


# Tabel dibuat otomatis saat modul dimuat (berlaku untuk `python app.py`
# maupun gunicorn / WSGI di hosting).
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
