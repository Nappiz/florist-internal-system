# Sistem Florist — Backend

Repository backend sistem internal bisnis florist pipe cleaner. Menggunakan Python 3.15.0, FastAPI, SQLAlchemy, PostgreSQL Supabase, dan Alembic. Fitur saat ini: health, login tanpa register publik, serta pengelolaan user.

## Struktur

```text
backend/
├── main.py
├── seed.py
├── .python-version
├── pyproject.toml
├── uv.lock
├── alembic.ini
├── .env.example
├── .gitignore
├── README.md
├── AGENTS.md
├── agent/
│   └── rules.md
├── configs/
│   ├── settings.py
│   ├── database.py
│   └── auth_dependencies.py
├── crud/
├── migration/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── models/
│   ├── base.py
│   ├── user_model.py
│   ├── auth_session_model.py
│   └── login_throttle_model.py
├── routes/
│   ├── health.py
│   ├── auth.py
│   └── users.py
├── schemas/
├── services/
├── tests/
│   ├── unit/
│   │   └── test_database/
│   │       └── test_get_database_url.py
│   └── endpoint/
├── use_cases/
├── .python/                    # Interpreter lokal, diabaikan Git
├── .tools/                     # Tool lokal, diabaikan Git
├── .uv-cache/                  # Cache uv lokal, diabaikan Git
└── .venv/                      # Virtual environment, diabaikan Git
```

`main.py` berada langsung di root repository backend, tanpa folder `app/`.

## Menjalankan

Gunakan uv versi terbaru. Jalankan dari root repository backend di PowerShell:

```powershell
$env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.python'
uv sync --locked
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --no-proxy-headers
```

Alternatif tanpa aktivasi virtual environment, setelah menjalankan setup di atas:

```powershell
uv run --locked uvicorn main:app --reload --no-proxy-headers
```

`.python-version` menentukan versi interpreter, `uv.lock` mengunci dependency, dan konfigurasi `cache-dir` pada `pyproject.toml` menyimpan cache di `.uv-cache/` dalam repository ini. Variabel `UV_PYTHON_INSTALL_DIR` menyimpan interpreter yang diunduh di `.python/` dalam repository ini.

Pada mesin ini, uv terbaru juga tersedia di `.tools/python-packages/bin/uv.exe`. Jika uv global belum diperbarui, gunakan executable lokal tersebut sebagai pengganti perintah `uv`:

```powershell
$env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.python'
& '.\.tools\python-packages\bin\uv.exe' sync --locked
```

Folder `.python/`, `.tools/`, `.uv-cache/`, dan `.venv/` adalah artefak lokal dan tidak ikut masuk repository. Clone baru dapat menggunakan uv yang terpasang pada mesin masing-masing.

## Endpoint

- `GET http://127.0.0.1:8000/health` → `{"status":"ok"}`
- Dokumentasi OpenAPI bawaan FastAPI: http://127.0.0.1:8000/docs

## Peran folder

| Folder | Peran saat fitur bisnis mulai dibuat |
| --- | --- |
| `configs` | Konfigurasi aplikasi dan environment. |
| `crud` | Operasi baca/tulis data. |
| `migration` | Perubahan skema database. |
| `models` | Model database. |
| `routes` | Endpoint health, auth, dan users. |
| `schemas` | Skema validasi request dan response. |
| `services` | Layanan pendukung dan integrasi. |
| `tests` | Pengujian aplikasi. |
| `use_cases` | Alur bisnis yang mengoordinasikan CRUD dan services. |

Setiap tabel memiliki file model sendiri. Query berada di `crud/`, logic dan transaksi per operasi berada di `use_cases/`, dan route hanya menangani batas HTTP.

## Database Supabase

Untuk clone baru, salin `.env.example` ke `.env` dan isi credential proyek sendiri. File `.env` lokal yang sudah ada tidak perlu ditimpa.

`DATABASE_URL` adalah connection string PostgreSQL dari dashboard Supabase → **Connect**. Gunakan **Direct connection** atau **Session pooler** port 5432 untuk setup ini. Jika jaringan tidak mendukung IPv6, gunakan Session pooler. Lihat [panduan koneksi Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres).

Gunakan password database dan URL-encode karakter khusus pada password. `SUPABASE_URL`, publishable key, secret key, dan JWKS URL merupakan credential API/Auth; SQLAlchemy menggunakan `DATABASE_URL`, bukan API key.

`configs/settings.py` membaca `.env` dari root backend dan juga menerima environment variable sistem; environment variable sistem memiliki prioritas. Nilai database URL dibungkus `SecretStr`. Variabel Supabase lain tetap boleh berada di `.env`.

`configs/database.py` menyiapkan engine PostgreSQL dengan driver psycopg, SSL (`sslmode=require`), pengecekan koneksi pool, dan timeout koneksi 10 detik. Engine dibuat saat pertama dipakai sehingga health tetap dapat berjalan tanpa koneksi database. Dependency `get_db` menyediakan SQLAlchemy session per request; gunakan `Depends(get_db)` saat endpoint bisnis mulai dibuat dan teruskan session ke use case. Use case mengatur transaksi dan memanggil `session.commit()` secara eksplisit untuk menyimpan perubahan.

## Alembic migration

Jalankan dari root backend setelah mengaktifkan virtual environment:

```powershell
alembic heads
alembic current
```

Saat model tabel bisnis mulai dibuat:

1. Turunkan model dari `models.base.Base` dan import model di `models/__init__.py` agar metadata terdaftar.
2. Generate revision:

   ```powershell
   alembic revision --autogenerate -m "create business tables"
   ```

3. Periksa file di `migration/versions/`, lalu terapkan perubahan yang sudah direview:

   ```powershell
   alembic upgrade head
   ```

Alembic menggunakan `DATABASE_URL` yang sama dari `.env`, tanpa menyimpan credential di `alembic.ini`. Tidak ada `create_all()` atau migration otomatis saat aplikasi startup. Revision `20261014_01` membuat tabel user, session, dan login throttle, beserta constraint, index, RLS, dan pembatasan akses Data API Supabase.

Autogenerate dibatasi pada schema default (`public`) dan mengabaikan tabel existing yang tidak terdaftar di metadata model aplikasi. Penghapusan tabel yang sengaja dikeluarkan dari model perlu ditulis secara eksplisit pada revision agar tabel Supabase atau aplikasi lain tidak ikut dihapus.

## Aturan agent dan pengujian

Agent wajib mengikuti [aturan backend](agent/rules.md), yang dirujuk oleh `AGENTS.md`. File dipisah per modul, satu tabel per file model, dan logic bisnis hanya berada di `use_cases/<modul>/<method>.py`.

Unit test dipisahkan dari endpoint test. Jalankan seluruh test dari root backend:

```powershell
python -m unittest discover -s tests -p "*_*.py" -v
```

Untuk menjalankan kategori tertentu:

```powershell
python -m unittest discover -s tests/unit -p "test_*.py" -v
# Jalankan setelah endpoint test ditambahkan
python -m unittest discover -s tests/endpoint -p "endpoint_*.py" -v
```

Test lokal menggunakan credential dummy dan database SQLite terisolasi. Endpoint test mengikuti pola `tests/endpoint/endpoint_<modul>/endpoint_<method>.py`. Unit test dipisah berdasarkan modul dan method.

Test concurrency PostgreSQL bersifat opt-in dan membuat schema sementara `auth_verify_<acak>`, lalu menghapus schema tersebut. Tabel aplikasi tidak digunakan sebagai data test:

```powershell
$env:RUN_POSTGRES_SECURITY_TESTS = '1'
python -m unittest discover -s tests/unit/test_auth -p "test_*.py" -v
Remove-Item Env:RUN_POSTGRES_SECURITY_TESTS
```

## Login dan user

Tidak ada endpoint register publik. Superadmin membuat akun user melalui `POST /users`; semua akun yang dibuat melalui API adalah user biasa. Flag superadmin tidak dapat diubah melalui API dan tetap melekat pada akun meski username diubah.

| Method | Endpoint | Akses |
| --- | --- | --- |
| POST | `/auth/login` | Login; membutuhkan header `Origin` yang diizinkan. |
| GET | `/auth/me` | User yang login; profil, CSRF token, dan waktu expiry. |
| POST | `/auth/logout` | User yang login; membutuhkan CSRF token. |
| POST | `/users` | Hanya superadmin; membuat user biasa. |
| GET | `/users?limit=20&offset=0` | Hanya superadmin; daftar user, maksimal 100 per request. |
| GET | `/users/{user_id}` | Superadmin atau pemilik akun. |
| PATCH | `/users/{user_id}` | Superadmin atau pemilik akun; edit username/password. |
| DELETE | `/users/{user_id}` | Hanya superadmin; akun superadmin tidak boleh dihapus. |

Username adalah 3–32 karakter ASCII: huruf, angka, `_`, `.`, atau `-`; karakter pertama huruf atau angka. Username dinormalisasi menjadi lowercase dan harus unik. Password adalah 8–128 karakter, dengan minimal satu huruf besar, satu huruf kecil, dan satu karakter spesial dari tanda baca ASCII. Password disimpan sebagai hash Argon2id.

Login memakai JSON berikut (nilai contoh, bukan credential seed):

```json
{"username":"staff","password":"ExamplePassword10@"}
```

Server mengirim cookie session **HttpOnly** dan response yang berisi profil publik, `csrf_token`, serta `expires_at`. Token session mentah tidak dikirim dalam JSON. Frontend harus memakai `credentials: "include"`; gunakan hostname yang sama untuk frontend dan backend ketika port berbeda, misalnya `localhost:3000` dan `localhost:8000`.

Untuk `POST /auth/logout`, `POST /users`, `PATCH /users/{id}`, dan `DELETE /users/{id}`, kirim `Origin` yang diizinkan dan `X-CSRF-Token` dari response login atau `/auth/me`. CSRF token terikat pada session; jangan simpan session token di localStorage.

Mengedit akun sendiri memerlukan `current_password`, termasuk superadmin saat mengedit akunnya sendiri:

```json
{"username":"newusername","password":"NewPassword10@","current_password":"CurrentPassword10@"}
```

`username` atau `password` boleh dikirim sendiri; setidaknya salah satu wajib diisi. Superadmin dapat mereset credential user lain tanpa current password milik target. Semua edit credential mencabut seluruh session target, sehingga user harus login lagi. Session memiliki expiry absolut **24 jam**, tidak diperpanjang oleh aktivitas. Logout mencabut session tersebut di database.

Percobaan login dan pemeriksaan current password berbagi batas 5 percobaan per username serta 30 per IP dalam 15 menit, termasuk percobaan berhasil. Batas disimpan di PostgreSQL agar berlaku lintas worker; ketika terlampaui, API mengembalikan 429 dan `Retry-After`. Password salah dan username tidak dikenal mengembalikan pesan yang sama.

## Seed superadmin

Setelah migration diterapkan:

```powershell
python seed.py
```

Script meminta password melalui prompt tersembunyi, atau membaca `SEED_SUPERADMIN_PASSWORD` dari environment lokal jika disediakan. Username awal adalah `superadmin`. Seed bersifat idempotent: tidak mereset password/username, tidak membuat superadmin kedua, dan tidak menaikkan role akun biasa yang kebetulan memakai nama tersebut. Password seed asli tidak ada di source atau `.env.example`.

## Konfigurasi keamanan

Default `APP_ENV` adalah `production`. Cookie menggunakan prefix `__Host-`, `Secure`, `HttpOnly`, host-only, dan `SameSite=Strict`. Production hanya menerima `ALLOWED_ORIGINS` HTTPS dan mengarahkan HTTP ke HTTPS. Isi hostname API yang tepat di `ALLOWED_HOSTS`; wildcard `*` ditolak.

Untuk development lokal secara eksplisit:

```dotenv
APP_ENV=development
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://localhost:8000","http://127.0.0.1:8000"]
ALLOWED_HOSTS=["localhost","127.0.0.1"]
```

Mode development menggunakan cookie non-Secure agar HTTP lokal bekerja. Jangan memakai mode ini pada deployment publik. CORS tidak memakai wildcard; perubahan data tetap memerlukan Origin dan CSRF yang valid. Validation error tidak mengembalikan input/password, response tidak boleh di-cache, dan request body dibatasi 16 KiB.

Untuk server yang diakses langsung, jalankan dengan `--no-proxy-headers`. Jika memakai reverse proxy untuk TLS, konfigurasikan proxy untuk menimpa header forwarded dari client dan batasi `--forwarded-allow-ips` hanya ke alamat proxy yang dipercaya. Jangan gunakan `*`: Uvicorn dapat mengganti client IP sebelum request mencapai aplikasi, sehingga header spoofing dapat melemahkan rate limit. Pengujian TestClient tidak menggantikan pemeriksaan konfigurasi proxy pada deployment sebenarnya.

Migration mengaktifkan RLS dan mencabut akses tabel autentikasi dari `PUBLIC`, `anon`, `authenticated`, serta `service_role`. Tabel ini hanya dipakai melalui koneksi database backend yang memiliki izin sesuai. Supabase REST API tidak digunakan untuk mengakses hash password atau session.

Keamanan transport, konfigurasi proxy, pembatasan trafik di gateway, dan penanganan credential produksi tetap harus diterapkan pada deployment; fitur ini tidak menjamin seluruh kemungkinan celah telah dieliminasi.

Hasil verifikasi fitur ini tercatat di [laporan pengujian keamanan](docs/security/user-auth-verification.md).
