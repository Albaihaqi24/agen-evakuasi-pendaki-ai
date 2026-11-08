# Penjelasan untuk laporan dan presentasi

## 1. Permasalahan

Jalur dengan jumlah pos paling sedikit bisa melewati medan berat atau bahaya.
Agen harus memutuskan jalur mana yang boleh dilewati terlebih dahulu, kemudian
memilih rute dengan akumulasi indeks beban terkecil.

## 2. PEAS

| Komponen | Implementasi |
|---|---|
| Performance | Tidak melintasi sisi yang ditutup; mencapai tujuan; meminimalkan cost |
| Environment | Graf 9 pos dan 11 jalur dua arah dengan fakta medan serta cuaca |
| Actuators | Rekomendasi urutan pos dan visualisasi penutupan jalur |
| Sensors | Pilihan cuaca, pos awal/tujuan, fakta medan dalam knowledge base |

Ini adalah problem solving agent berbasis model. Pembaruan input memicu
inferensi dan perencanaan ulang. Model lingkungan disederhanakan menjadi graf
statis pada satu siklus pencarian, dengan cuaca yang bisa diubah antar siklus.

## 3. Formulasi masalah

- **State:** ID pos saat ini.
- **Initial state:** S, atau pos pilihan pengguna.
- **Actions:** bergerak melalui sisi terbuka ke pos tetangga.
- **Transition:** pindah dari u ke v pada graf dua arah.
- **Goal test:** ID pos sama dengan tujuan, default G.
- **Path cost:** jumlah jarak + beban medan + penalti kabut seluruh sisi rute.

## 4. Forward Chaining

Fakta awal berasal dari medan per sisi dan cuaca skenario. Mesin menerapkan
aturan yang premisnya terpenuhi, memasukkan kesimpulan baru, lalu mengulang
sampai tidak ada fakta baru. Setiap penerapan aturan dicatat agar bisa dijelaskan.

| Aturan | Premis | Kesimpulan |
|---|---|---|
| R1 | hujan_lebat AND medan_curam | risiko_longsor |
| R2 | hujan_lebat AND jalur_sungai | risiko_banjir_bandang |
| R3 | kabut_tebal AND tepi_jurang | risiko_tersesat_jatuh |
| R4 | salah satu risiko di atas | JALUR_DITUTUP |
| R5 | kabut_tebal AND NOT JALUR_DITUTUP | penalti cost +1 |

R4 direpresentasikan sebagai tiga aturan positif yang menuju kesimpulan sama.
R5 memakai negasi dan baru dijalankan sesudah seluruh inferensi bahaya selesai.
Hal ini mencegah penambahan penalti pada sisi yang seharusnya ditutup.
Setiap sisi tertutup dihilangkan dari graf pencarian dalam kedua arah.

Contoh S–C saat ekstrem: fakta hujan_lebat + medan_curam memicu R1, lalu
risiko_longsor memicu R4. A* dan BFS sama-sama tidak mendapat akses ke sisi ini.
Pada S–E yang landai, kabut hanya memicu R5: bobot dasar 2 menjadi 3.

## 5. A* Search

A* memakai priority queue dengan f(n)=g(n)+h(n). g adalah akumulasi cost aktual,
h adalah estimasi cost tersisa. Setiap penemuan cost yang lebih rendah memperbarui
parent dan memasukkan kandidat baru. Kandidat lama dengan cost usang dilewati.
Rute dibentuk dengan menelusuri parent dari tujuan ke awal.

Heuristic menggunakan jarak koordinat skematik yang diskalakan /1000.
Semua sisi memenuhi w(u,v) >= d(u,v)/1000. Karena ketaksamaan segitiga,
h(u) <= w(u,v)+h(v) dan h(goal)=0. Maka heuristic konsisten, dan juga admissible.
Pengujian membandingkan hasil A* dengan Floyd–Warshall sebagai oracle independen.

## 6. Perbandingan BFS

BFS menggunakan FIFO queue. Pos yang lebih dekat dalam jumlah sisi dikunjungi
lebih dahulu. BFS tidak menggunakan bobot untuk menentukan urutan eksplorasi.
Cost baru dihitung untuk rute hasilnya. Perbandingan kedua algoritma memakai
graf aman yang sama, sehingga perbedaan berasal dari strategi pencarian.

Ekstrem: BFS mengambil S–A–B–G dengan bobot 5+6+5=16.
A* mengambil S–E–F–H–G dengan bobot 3+3+3+3=12.
A* menghemat 4 indeks beban (25%), meskipun melewati satu sisi tambahan.

## 7. Rencana demonstrasi singkat

1. Buka dashboard pada skenario ekstrem. Tunjukkan tiga sisi merah dan alasan R1–R4.
2. Tunjukkan hasil A* 12 dan BFS 16, lalu ganti tampilan rute untuk membandingkan.
3. Pilih cerah. Jalur S–C–D–G terbuka dan A* memperoleh cost 3.
4. Pilih kabut. Jelaskan penutupan C–F dan penalti +1 pada sisi yang terbuka.
5. Kembali ke ekstrem. Klik S–A, S–E, dan S–C untuk menutup manual semua akses S.
   Tunjukkan bahwa agen melaporkan tidak ada rute, bukan memaksakan jalur bahaya.
6. Reset dan ekspor hasil JSON untuk dokumentasi.

## 8. Kesimpulan dan batasan

Rule-Based Reasoning menentukan kelayakan jalur menurut aturan yang tersedia,
dan A* mengoptimalkan cost pada graf hasil penyaringan. Dataset dirancang untuk
mereproduksi contoh angka pada PPT, sehingga hasil ini bukan validasi operasional
SAR. Pengembangan berikutnya dapat memakai data jalur terverifikasi, cuaca lokal
per segmen, dan aturan tambahan yang ditentukan bersama ahli terkait.
