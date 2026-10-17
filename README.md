# Sistem Florist Backend

Backend PRD v1.0 + v2.0 Phase 1 dan 3: Python 3.15, FastAPI, SQLAlchemy, PostgreSQL Supabase, Alembic. `main.py` tetap di root, tanpa folder `app/`.

Modul tersedia: Auth/Users, Materials, Suppliers, Supplier Material Listings, Purchases/Payments, Inventory, Flowers/BOM, Products/BOM, Orders/Production/Payments, Dashboard, Reports, Audit, Custom Bouquets/Options/Settings, Operational Expenses dan Cashflow. Tidak ada public catalog/order form.

## Menjalankan

Dari root backend di PowerShell:

```powershell
$env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.python'
& '.\.tools\python-packages\bin\uv.exe' sync --locked
.\.venv\Scripts\Activate.ps1
alembic upgrade head
uvicorn main:app --reload --no-proxy-headers
```

Uv global juga boleh digunakan. `.python/`, `.tools/`, `.uv-cache/`, `.venv/`, `.backups/` dan `.env` tidak ikut Git. Dependency dikunci di `uv.lock`.

Untuk clone baru, salin `.env.example` ke `.env`, isi `DATABASE_URL` PostgreSQL Supabase Direct atau Session pooler port 5432, dan atur origin/host. Jangan menimpa `.env` yang sudah berisi credential. Koneksi SQLAlchemy memakai SSL, parameter log disembunyikan, dan API key Supabase bukan pengganti password database.

- Health: `GET http://127.0.0.1:8000/health`
- Swagger: http://127.0.0.1:8000/docs
- Kontrak JSON: http://127.0.0.1:8000/openapi.json
- Endpoint bisnis: `/api/v1`

## Struktur dan aturan

Satu tabel per file `models/`, satu modul per file `crud/`, `routes/`, `schemas/`; business logic dan transaksi di `use_cases/<modul>/<operasi>.py`. `crud/` hanya akses database. `configs/` konfigurasi teknis, `services/` I/O/security, `migration/` Alembic. Ikuti `AGENTS.md` dan `agent/rules.md`.

Tests dipisahkan menjadi `tests/unit/test_<modul>/` dan `tests/endpoint/endpoint_<modul>/`. Runtime tidak membuat tabel atau menjalankan migration otomatis saat startup.

## Autentikasi dan akses

Tidak ada registrasi publik. Login memakai username atau email melalui field JSON `username`; password disimpan dengan Argon2id. Session cookie HttpOnly berlaku absolut 24 jam. Semua mutasi membutuhkan Origin tepercaya dan X-CSRF-Token dari login atau `/api/v1/auth/me`.

Superadmin mengelola semua akun/role/status, melihat audit global, dan membuat adjustment stok. Staff mengelola operasional dan hanya mengubah profil/credential sendiri. Role/status dibaca ulang setiap request. Minimal satu superadmin aktif harus tersisa, termasuk saat perubahan bersamaan. Delete user menonaktifkan akun dan mempertahankan histori.

Password minimal 8 karakter, maksimal 128, dengan huruf besar, huruf kecil, dan karakter khusus. Perubahan username/password sendiri membutuhkan current_password; perubahan credential dan disable mencabut session. Login dibatasi 5 percobaan per akun dan 30 per IP selama 15 menit, lintas worker.

Seed hanya untuk instalasi awal:

```powershell
python seed.py
```

Password diminta lewat prompt tersembunyi atau SEED_SUPERADMIN_PASSWORD. Profil awal dapat diatur lewat SEED_SUPERADMIN_FULL_NAME/EMAIL. Seed tidak mereset credential atau profil akun existing. Tidak ada password asli dalam source. Akun lama diberi full_name dari username dan email placeholder `username@legacy.invalid` saat migrasi; edit email/profil tersebut melalui API jika diperlukan.

## Migrasi PRD dan kompatibilitas

Revision `a11c6331bb7c` menambah tabel normal serta profil/role/status user. Revision `20261015_05` memperketat batas angka inventory. Revision `20261017_06` menambah Custom Bouquets dan Finance; total 37 tabel aplikasi. Seluruh tabel aplikasi memiliki RLS dan tidak memberikan grant CRUD kepada PUBLIC/anon/authenticated/service_role. Akses data melalui backend SQLAlchemy.

Tabel riset lama `suppliers` dipertahankan. Data disalin ke `materials`, `supplier_stores`, dan `supplier_materials` menggunakan identitas deterministik; toko dan bahan yang sama digabung berdasarkan atribut sumber. Harga pecahan lama dibulatkan half-up ke rupiah pada listing baru, sedangkan nilai asli tetap di tabel lama. Stok awal hasil migrasi nol, tanpa mengarang penerimaan barang.

`GET /suppliers`, `GET /suppliers/{id}`, `GET /expenses`, dan detail expenses tetap tersedia sebagai arsip. POST/PATCH/DELETE pada endpoint lama mengembalikan 410 setelah pemeriksaan autentikasi/CSRF. Pembelian operasional menggunakan `/api/v1/purchases`, bukan expenses. Auth dan Users tanpa prefix masih menjadi alias kompatibilitas; list user lama berbentuk array, list v1 berbentuk page.

Downgrade PRD ditolak jika sudah ada transaksi/aktivitas baru. Gunakan backup, restore terisolasi, atau perbaikan ke depan, bukan menghapus data produksi.

## Panduan API dan frontend

Lihat [kontrak dan aturan bisnis](docs/backend-api.md), [penyesuaian frontend](docs/frontend-adjustments.md), [backup/recovery](docs/operations.md), [PRD sumber](docs/product-requirements.md), dan [hasil verifikasi](docs/security/prd-verification.md).

Untuk PRD2, lihat [kontrak v2 dan penyesuaian frontend](docs/backend-api-v2.md). Pembayaran Order/Purchase baru wajib memilih cash_account_id. Modul frontend PRD1 yang sudah ada tetap dipertahankan; UI custom/finance dan relay barunya belum ditambahkan.

## Pengujian

```powershell
python -m unittest discover -s tests -p '*_*.py' -v
```

SQLite terisolasi dipakai untuk tes lokal. Untuk semua pengujian termasuk concurrency PostgreSQL:

```powershell
$env:RUN_POSTGRES_SECURITY_TESTS = '1'
python -m unittest discover -s tests -p '*_*.py' -v
Remove-Item Env:RUN_POSTGRES_SECURITY_TESTS
```

Tes PostgreSQL membuat schema acak `auth_verify_<acak>` atau `migration_verify_<acak>` dan membersihkannya setelah selesai; tidak memakai baris bisnis public. Rehearsal migrasi memverifikasi upgrade, copy data dummy dan rollback yang menjaga tabel sumber. Kesesuaian skema dan proteksi Supabase:

```powershell
alembic check
python -m scripts.verify_prd_database
```

## Deployment

APP_ENV default production memakai cookie Secure dengan prefix __Host-, HTTPS dan origin/host eksplisit. Development HTTP lokal harus memilih APP_ENV=development. Request JSON biasa maksimum16 KiB, konfigurasi builder/backfill tertentu256 KiB; raw receipt POST ke endpoint khusus maksimal5 MiB. Reverse proxy harus menimpa forwarded headers dan Uvicorn hanya mempercayai IP proxy tertentu. HTTPS, backup terjadwal, secret management, monitoring, serta pengujian performa pada deployment merupakan konfigurasi operasional terpisah.

Receipt JPG/PNG/PDF disimpan privat di PRIVATE_RECEIPT_DIR dan perlu ikut backup. Expenses operasional dan full payment reversal/refund kini tersedia pada PRD2; retur barang, reservasi, penerimaan/produksi parsial dan stok barang jadi tetap di luar cakupan.
