# Agen Cerdas Evakuasi Pendaki Gunung Saat Cuaca Ekstrem

Mini Project Artificial Intelligence • Python • Forward Chaining + A* Search

Implementasi berdasarkan PPT dan PDF tugas yang dilampirkan. Seluruh pos, jarak,
cuaca, dan bobot adalah data sintetis untuk simulasi akademik, bukan data lapangan.
Program berjalan tanpa API key, database, atau layanan berbayar. Dashboard
Streamlit memerlukan instalasi dependensi dan koneksi internet untuk deployment.

## Mulai di Windows / VS Code

1. Instal Python **3.10 atau lebih baru** dan aktifkan opsi **Add Python to PATH** serta **Tcl/Tk and IDLE** pada installer. Tcl/Tk hanya diperlukan untuk aplikasi desktop.
2. Ekstrak ZIP terlebih dahulu. Buka folder `mountain-sar-evacuation-ai` melalui **File → Open Folder** di VS Code.
3. Pilih **Terminal → New Terminal**. Jalankan:

```powershell
python main.py
```

Jika `python` tidak dikenali, coba `py -3 main.py`. Bisa juga klik dua kali
`JALANKAN_WINDOWS.bat`.

## Dashboard web lokal

Pasang dependensi dan jalankan dari root proyek:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run web_app.py
```

Jika `python` tidak dikenali, gunakan `py -3` sebagai penggantinya. Anda juga
bisa klik dua kali `JALANKAN_WEB_WINDOWS.bat`; file tersebut mengubah working
directory ke folder tempat file BAT berada sebelum menjalankan Streamlit.
Streamlit akan mencetak alamat lokal, biasanya `http://localhost:8501`.

Dashboard web menggunakan modul simulasi yang sama dengan desktop dan
menyediakan pemilihan cuaca/pos, penutupan jalur manual, graf berwarna,
perbandingan A*/BFS, jejak aturan, dan unduhan JSON. Pada skenario ekstrem
default S ke G, A* menghasilkan cost 12 dan BFS cost 16.

### Berbagi dashboard melalui tautan publik

Untuk hosting gratis, gunakan Streamlit Community Cloud. Siapkan repository
GitHub berisi proyek ini, lalu pada Streamlit Community Cloud pilih **Create
app**, hubungkan GitHub, pilih repository/branch, dan isi **Main file path**
dengan `web_app.py`. Deployment menghasilkan tautan publik HTTPS setelah
berhasil selesai. Tidak diperlukan kartu pembayaran untuk penggunaan free
tier, tetapi akun GitHub dan Streamlit diperlukan. Tautan publik tersebut
berjalan di hosting, sehingga tidak bergantung pada laptop menyala. Tautan
belum ada sampai aplikasi benar-benar dideploy; jangan membagikan alamat
localhost karena hanya dapat diakses dari komputer sendiri.

Pada Linux dengan modul Tkinter terpisah, pasang paket Tkinter distribusi Anda,
atau gunakan mode CLI tanpa GUI. Pada macOS gunakan Python yang menyertakan Tk.

## Cara menggunakan dashboard

- Pilih cuaca `cerah`, `hujan`, `kabut`, atau `ekstrem`.
- Pilih pos awal dan tujuan. Default S (Puncak Bayangan) menuju G (Basecamp Utama).
- Hasil langsung diperbarui. Pilih A* atau BFS untuk mengganti rute pada peta.
- Garis hijau menunjukkan rute pilihan, merah putus menunjukkan jalur ditutup.
- Klik garis atau angka bobot untuk menutup/membuka manual sisi tersebut.
  Membuka manual tidak menimpa penutupan yang disimpulkan dari cuaca.
- Panel kanan menampilkan alasan penutupan, rincian cost, dan tabel ekspansi A*.
- **Ekspor JSON** menyimpan input dan hasil lengkap. **Reset** mengembalikan skenario awal.
- Jika semua akses terputus, aplikasi menampilkan **TIDAK ADA RUTE TERSEDIA**.

## Mode terminal

```powershell
python main.py --cli
python main.py --cli --scenario cerah
python main.py --cli --scenario ekstrem --start S --goal G --output hasil.json
python -m unittest discover -s tests -v
```

## Hasil utama sesuai PPT

| Skenario | Penutupan otomatis | Rute A* | Cost A* | Rute BFS | Cost BFS |
|---|---|---|---:|---|---:|
| Cerah | Tidak ada | S–C–D–G | 3 | S–A–B–G | 13 |
| Hujan | S–C, C–D | S–E–F–H–G | 8 | S–A–B–G | 13 |
| Kabut | C–F | S–C–D–G | 6 | S–A–B–G | 16 |
| Ekstrem | S–C, C–D, C–F | S–E–F–H–G | **12** | S–A–B–G | **16** |

Pada kondisi ekstrem A* memerlukan 4 langkah dan BFS 3 langkah. Cost A* lebih
rendah 25%. BFS mengutamakan jumlah sisi, sehingga tidak menjamin cost minimum.
Urutan tetangga mengikuti urutan sisi pada `knowledge_base.py`; jika beberapa
rute BFS memiliki jumlah langkah sama, urutan ini menentukan rute yang dipilih.

## Struktur

```text
mountain-sar-evacuation-ai/
  main.py
  web_app.py                 dashboard Streamlit untuk browser
  JALANKAN_WINDOWS.bat
  JALANKAN_WEB_WINDOWS.bat
  requirements.txt
  README.md
  PENJELASAN_PROYEK.md
  HASIL_PENGUJIAN.txt
  examples/                   hasil JSON empat skenario
  src/
    knowledge_base.py         pos, sisi, fakta medan, heuristic
    reasoning_engine.py       aturan R1–R5 dan pembentukan graf aman
    search_agent.py           A* dan BFS
    simulation.py             integrasi reasoning dan search
    visualizer.py             dashboard Tkinter
  tests/test_agent.py          pengujian algoritma dan integrasi
  tests/test_web_app.py        smoke test dashboard Streamlit
```

## Bobot dan heuristic

`cost(sisi) = jarak + beban_medan + penalti_kabut`.
Satuan akhirnya adalah indeks beban simulasi, bukan menit atau kilometer murni.
Kabut menambah 1 per sisi terbuka. Bahaya menutup sisi sepenuhnya.

`h(n) = jarak Euclidean koordinat skematik(n, tujuan) / 1000`.
Skala dipilih agar setiap bobot sisi setidaknya sebesar jarak skematik sisi / 1000.
Dengan ketaksamaan segitiga, h konsisten dan admissible untuk seluruh tujuan.
Menutup sisi atau menambah penalti tidak merusak sifat tersebut. Heuristic ini
konservatif, sehingga A* belum tentu mengekspansi lebih sedikit node dibanding BFS.
Optimalitas yang diuji adalah total cost, bukan jumlah ekspansi.

## Penyesuaian data

Edit `NODES` dan `EDGES` di `src/knowledge_base.py`. Data graf dua arah.
`Edge(u,v,jarak,beban_medan,fakta)` menyimpan fakta lokal per segmen.
Cuaca preset diterapkan ke seluruh segmen pada setiap analisis ulang.
Jika koordinat/bobot diubah, pertahankan syarat skala heuristic atau gunakan
h=0 sebagai baseline Dijkstra. Jalankan pengujian kembali setelah perubahan.

## Batas implementasi

Sensor GPS/cuaca pada PEAS dimodelkan sebagai input simulasi manual. Program
belum terhubung ke GPS, sensor fisik, peta nyata, maupun cuaca langsung. Angin
kencang disebut sebagai konteks pada PPT, tetapi tidak memiliki aturan R1–R5,
sehingga tidak ditambahkan sebagai aturan baru. Status terbuka berarti tidak
terblokir oleh aturan yang dimodelkan, bukan jaminan keselamatan lapangan.

Jika GUI gagal karena display/Tkinter tidak tersedia, gunakan `--cli`.
