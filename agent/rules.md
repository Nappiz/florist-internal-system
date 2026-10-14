# Aturan pengembangan backend

Aturan ini wajib diikuti setiap agent yang mengerjakan repository backend.

## 1. Pisahkan file berdasarkan modul

- Jangan menggabungkan beberapa fitur atau modul ke dalam satu file.
- Di `models/`, satu tabel database harus memiliki satu file model sendiri, misalnya `user_model.py` dan `order_model.py`. Jangan menaruh beberapa tabel dalam satu file. `base.py` hanya berisi base ORM, bukan kumpulan tabel.
- Di `crud/`, satu modul memiliki satu file CRUD, misalnya `users_crud.py` dan `orders_crud.py`.
- Di `schemas/`, satu modul memiliki satu file schema, misalnya `user_schema.py` dan `order_schema.py`. Schema request dan response untuk modul yang sama boleh berada dalam file modul tersebut.
- Di `routes/`, satu modul memiliki satu file route. Nama file cukup nama modul, misalnya `users.py` dan `orders.py`; jangan tambahkan suffix `_route` atau `_routes`.
- File `__init__.py` digunakan untuk deklarasi package atau import, bukan untuk menumpuk implementasi modul.

## 2. CRUD tanpa logic bisnis; logic hanya di use case

- CRUD **TIDAK BOLEH** berisi logic bisnis. Isinya hanya operasi akses database: build query, execute query, dan mengembalikan hasil query.
- Jangan menaruh perhitungan keuntungan, validasi aturan bisnis, keputusan berdasarkan kondisi bisnis, atau koordinasi alur fitur di CRUD.
- Logic bisnis **HANYA BOLEH** berada di `use_cases/`. Routes, schemas, models, dan services tidak boleh mengambil alih logic tersebut.
- `use_cases/` adalah nama folder yang digunakan repository ini. Setiap modul memiliki subfolder sendiri; setiap method atau operasi logic memiliki file sendiri.
- Routes hanya menangani batas HTTP: menerima request, memasok dependency, memanggil use case, dan mengembalikan response. Schemas menangani bentuk dan tipe data. Services menangani integrasi atau I/O pendukung. Konfigurasi teknis tetap di `configs/`.
- Koordinasi transaksi dan penyimpanan perubahan (`commit`/`rollback`) dilakukan oleh use case, bukan oleh CRUD atau route.

Contoh struktur:

```text
models/
├── user_model.py
└── order_model.py
crud/
├── users_crud.py
└── orders_crud.py
schemas/
├── user_schema.py
└── order_schema.py
routes/
├── users.py
└── orders.py
use_cases/
└── transaction/
    ├── get_transaction.py
    ├── post_transaction.py
    └── update_transaction.py
```

## 3. Pisahkan unit test dan endpoint test

- Unit test berada di `tests/unit/`. Setiap modul memiliki folder `test_<modul>/`, dan setiap method memiliki file `test_<method>.py`.
- Endpoint test berada di `tests/endpoint/`. Setiap modul memiliki folder `endpoint_<modul>/`, dan setiap method memiliki file `endpoint_<method>.py`.
- Jangan mencampurkan unit test dan endpoint test dalam satu folder atau file.
- Beberapa skenario untuk method yang sama boleh berada di satu file test method tersebut.
- Tambahkan `__init__.py` pada subfolder test agar discovery `unittest` dapat menelusurinya.

Contoh struktur:

```text
tests/
├── unit/
│   └── test_transaction/
│       ├── test_get_transaction.py
│       ├── test_post_transaction.py
│       └── test_update_transaction.py
└── endpoint/
    └── endpoint_transaction/
        ├── endpoint_get_transaction.py
        ├── endpoint_post_transaction.py
        └── endpoint_update_transaction.py
```

Jalankan dari root backend:

```powershell
# Seluruh unit test dan endpoint test
python -m unittest discover -s tests -p "*_*.py" -v

# Unit test saja
python -m unittest discover -s tests/unit -p "test_*.py" -v

# Endpoint test saja, setelah folder ini memiliki test
python -m unittest discover -s tests/endpoint -p "endpoint_*.py" -v
```

Endpoint test menggunakan prefix `endpoint_`, sehingga discovery khusus endpoint wajib menggunakan pattern `endpoint_*.py`. Discovery seluruh test menggunakan `*_*.py` agar kedua kategori ditemukan.
