# DOKUMEN SPESIFIKASI PROTOTIPE UAS: AGEN NAVIGASI CERDAS KAMPUS MENGGUNAKAN ALGORITMA A* SEARCH BERBASIS DATA GEOSPASIAL RIIL

* **Mata Kuliah:** Artificial Intelligence (AI) — Semester 5 (Kurikulum OBE)
* **Program Studi:** Teknik Informatika, UIN Maulana Malik Ibrahim Malang
* **Judul Proyek:** Rancang Bangun Agen Navigasi Cerdas Rute Antar-Gedung Kampus Menggunakan Algoritma A* Search Berbasis Data Geospasial Riil
* **Tim Pengembang:**
  1. Ahmed Yasser Luma' Nashril Ilah (240605110152)
  2. Fahmi Zaki Darmawan (240605110239)
  3. Muhammad Jalaluddin (240605110235)
* **Status Berkas:** **PROTOTIPE TAHAP UAS (FINAL & TERVERIFIKASI)**
* **Lokasi Modul:** `D:\3. TUGAS & MATERI\SMT 5\ARTIFICIAL INTELLIGENCE\algorithm_project\`

---

## 1. Identitas & Latar Belakang Pengembangan Tahap UAS

Pada tahap sebelumnya (UTS), sistem berfokus pada proposal konseptual dan model simulasi 12 simpul nominal. Pada **Tahap UAS**, agen navigasi cerdas ini ditingkatkan secara signifikan menjadi sistem produksi fungsional berbasis:
1. **Objek Geospasial Riil (OOP):** Mengganti simpul teks menjadi entitas kelas `Gedung` berbasis *Object-Oriented Programming* dengan data koordinat GPS (Latitude & Longitude) asli Google Maps dari 36 fasilitas Kampus 1 UIN Maulana Malik Ibrahim Malang.
2. **Satuan Jarak Riil Meter (Formula Haversine):** Menggunakan formula matematis Haversine dengan radius kelengkungan bumi $R = 6.371.000$ meter.
3. **Topologi Pejalan Kaki Nyata (63 Ruas Jalan):** Menghubungkan 36 fasilitas melalui koridor, lorong asrama ma'had, boulevard rektorat, dan lapangan.
4. **Fitur Rintangan Dinamis (*Dynamic Obstacle & Re-routing*):** Simulasi penutupan jalan sementara secara interaktif (`tutup_jalan` dan `buka_jalan`) di mana agen A* secara adaptif menghitung lintasan memutar tercepat.
5. **Evaluasi Tiga Algoritma (A* vs UCS vs BFS):** Pembuktian optimalitas biaya jalur riil (UCS sebagai ground truth) dan pembuktian empiris ketidakoptimalan jarak BFS pada graf berbobot meter.

---

## 2. Struktur Modul Prototipe UAS

```text
algorithm_project/
├── gedung.py               # Entitas OOP Gedung, formula Haversine, parser Excel mandiri & data cleansing
├── campus_network.py       # Topologi 36 gedung & 63 ruas jalan, verifikasi BFS, rintangan dinamis
├── search_engine.py        # Algoritma pencarian: A* Search, UCS (Dijkstra), BFS, & All-Pairs verifier
├── visualize_campus.py     # Visualisasi graf 2D spasial berbasis koordinat GPS nyata dengan Matplotlib
├── main_uas_demo.py        # Titik masuk CLI: 3 skenario nyata, tabel metrik komparasi, demo rintangan dinamis
├── test_campus_network.py  # Suite 25 unit test & uji regresi otomatis (100% PASS dalam 0.26 detik)
├── data_gedung.xlsx        # Sumber data primer 36 fasilitas Kampus 1 UIN Malang
└── peta_kampus_rute.png    # Hasil render visualisasi spasial peta kampus dan rute solusi
```

---

## 3. Data Cleansing & Integritas Geospasial

Sistem membaca langsung berkas mentah `data_gedung.xlsx` menggunakan pustaka bawaan Python (`zipfile` dan `xml.etree.ElementTree`) tanpa memerlukan pustaka eksternal pihak ketiga (`openpyxl`), dengan aturan pembersihan data:
1. **Fakultas Ekonomi (ID 22):** Nilai Longitude mentah tertulis `'11.2.606784'` (kesalahan ketik tanda titik ganda) berhasil dibersihkan menjadi `112.606784`.
2. **Mabna Al-Ghozali (ID 9):** Nilai Latitude mentah tertulis `-7.94048` (salah ketik kurang angka 9, berjarak 1 km dari kampus) berhasil diselaraskan dengan posisi gugus Ma'had Putra menjadi `-7.949048`.
3. **Pembersihan Whitespace & Title Case:** Nama fasilitas dinormalisasi dari spasi berlebih menggunakan regex dan diformat seragam.
4. **Type-Safety:** Mencegah injeksi nilai boolean pada koordinat numerik melalui validasi tipe eksplisit.

---

## 4. Landasan Teori AI: Admissibility & Consistency Heuristik

Fungsi evaluasi A* didefinisikan sebagai:
$$f(n) = g(n) + h(n)$$

* $g(n)$: Biaya akumulasi jarak riil jalan kaki dari simpul awal ke simpul $n$ (dalam satuan meter).
* $h(n)$: Estimasi jarak garis lurus bola bumi dari simpul $n$ ke simpul tujuan (Haversine distance).
* **Jaminan Admissibility ($h(n) \le h^*(n)$):** Karena jarak lengkung bumi merupakan batas bawah mutlak (*absolute geodesic lower bound*) dari setiap jalan kaki pejalan kaki yang berbelok melintasi kontur kampus, dan bobot ruas jalan memenuhi $w(u, v) \ge \text{Haversine}(u, v)$ (dengan faktor kelokan pedestrian 10%), maka $h(n)$ **terbukti 100% Admissible**.
* **Jaminan Consistency/Monotonicity ($h(u) \le w(u, v) + h(v)$):** Berdasarkan ketidaksamaan segitiga bola (*Spherical Triangle Inequality*), nilai $f(n)$ di sepanjang lintasan dijamin tidak pernah menurun monoton, sehingga A* tidak perlu mengevaluasi ulang simpul yang sudah ditutup (*no re-opening*).

---

## 5. Hasil Verifikasi Komputasional Prototipe UAS

### A. Uji Menyeluruh All-Pairs (1.260 Rute Lintas Kampus)
Berdasarkan eksekusi pengujian terhadap seluruh kombinasi $36 \times 35 = 1.260$ pasangan gedung:
* **Tingkat Keberhasilan:** 100.0% (1.260 / 1.260 pasangan sukses terhubung).
* **Kesesuaian Optimalitas Biaya A* vs UCS:** **0 Mismatch (100% Identik Biaya)**.
* **Efisiensi Penelusuran Simpul A* terhadap UCS:**
  * A* mengekspansi lebih sedikit simpul pada **1.216 pasangan (96.5%)**.
  * A* mengekspansi simpul sama banyak pada **44 pasangan (3.5%)** (hanya pada pasangan yang bertetangga langsung).
  * A* **tidak pernah sekalipun** mengekspansi lebih banyak simpul dibanding UCS (**0.0%**).
  * Total ekspansi simpul: A* = **9.830 simpul** vs UCS = **22.680 simpul** (penghematan **56.7%** simpul).
* **Pembuktian Empiris Sub-optimalitas BFS:**
  * BFS menghasilkan rute meter yang **suboptimal pada 627 pasangan (49.8%)**, membuktikan bahwa BFS hanya meminimalkan jumlah langkah (*hop count*), bukan jarak fisik meter.

### B. Hasil Tiga Skenario Navigasi Riil
1. **Skenario 1: Jarak Dekat** (Mabna Farobi [1] $\to$ Kantin Al-Kautsar [4]):
   * Jarak: **115.6 meter** (2 langkah)
   * Simpul Diekspansi: A* = **2 simpul** vs UCS = **3 simpul** (hemat **33.3%**)
2. **Skenario 2: Jarak Menengah** (Pos Satpam Ma'had [10] $\to$ Fak. Saintek [18]):
   * Jarak: **186.2 meter** (4 langkah)
   * Simpul Diekspansi: A* = **5 simpul** vs UCS = **13 simpul** (hemat **61.5%**)
3. **Skenario 3: Jarak Jauh Lintas Kampus** (Mabna Farobi [1] $\to$ Gedung SC / Sport Center [29]):
   * Jarak Optimal (A* & UCS): **655.7 meter** (11 langkah)
   * Rute BFS: **720.7 meter** (10 langkah — **lebih panjang 65.0 meter** dari A*)
   * Simpul Diekspansi: A* = **22 simpul** vs UCS = **30 simpul** (hemat **26.7%**)

### C. Simulasi Rintangan Dinamis (*Dynamic Obstacle*)
Pada lintasan langsung antara **Masjid Tarbiyah [13]** dan **Fakultas Saintek [18]**:
* Kondisi Normal: **86.9 meter** (1 langkah langsung).
* Ditutup Sementara (`graph.tutup_jalan(13, 18)`): Agen A* secara otomatis mengalihkan rute melalui Menara UIN Malang sepanjang **96.3 meter** (2 langkah).
* Dibuka Kembali (`graph.buka_jalan(13, 18)`): Rute kembali optimal ke jalur langsung (**86.9 meter**).

---

## 6. Panduan Menjalankan Prototipe UAS

Jalankan perintah-perintah berikut melalui terminal PowerShell:

```powershell
# 1. Menjalankan demonstrasi lengkap Prototipe UAS (3 Skenario, Dynamic Obstacle, & Plot Peta)
python "main_uas_demo.py"

# 2. Menjalankan suite 25 Unit Tests otomatis
python -m unittest "test_campus_network.py" -v

# 3. Menampilkan daftar 36 fasilitas kampus hasil cleansing data geospasial
python "main_uas_demo.py" --list-gedung

# 4. Menjalankan verifikasi komparatif menyeluruh seluruh 1.260 pasangan gedung
python "main_uas_demo.py" --verify-all

# 5. Mencari rute kustom antar gedung dengan visualisasi peta gambar
python "main_uas_demo.py" --start "Masjid Tarbiyah" --goal "Fakultas Saintek" --visualize
```
