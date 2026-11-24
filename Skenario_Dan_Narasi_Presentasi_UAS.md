# PANDUAN SKENARIO, PEMBAGIAN PERAN, DAN NARASI PRESENTASI TAHAP UAS

* **Mata Kuliah:** Artificial Intelligence (AI) — Semester 5 (Kurikulum OBE)
* **Program Studi:** Teknik Informatika, UIN Maulana Malik Ibrahim Malang
* **Judul Proyek:** Rancang Bangun Agen Navigasi Cerdas Rute Antar-Gedung Kampus Menggunakan Algoritma A* Search Berbasis Data Geospasial Riil
* **Tim Penyusun:**
  1. **Ahmed Yasser Luma' Nashril Ilah (240605110152)** — Pembicara 1 & Moderator
  2. **Fahmi Zaki Darmawan (240605110239)** — Pembicara 2 (Teori AI & Algoritma)
  3. **Muhammad Jalaluddin (240605110235)** — Pembicara 3 (Implementasi Teknis & Live Demo)
* **Durasi Standar:** 12 – 15 Menit (Presentasi + Demonstrasi Langsung CLI)

---

## 1. Matriks Pembagian Peran & Timeline Presentasi

| Sesi | Alokasi Waktu | Pembicara | Topik Bahasan Utama |
|:---|:---:|:---|:---|
| **Sesi 1** | Menit 00.00 – 03.30 | **Ahmed Yasser** (Pembicara 1) | Pembukaan, Latar Belakang, Transisi Tahap UTS $\to$ UAS, Ekstraksi & Data Cleansing Geospasial 36 Gedung. |
| **Sesi 2** | Menit 03.30 – 07.30 | **Fahmi Zaki** (Pembicara 2) | Formula Haversine, Landasan Teori AI (Admissibility & Consistency), serta Analisis Tiga Algoritma (A*, UCS, BFS). |
| **Sesi 3** | Menit 07.30 – 11.30 | **Muhammad Jalaluddin** (Pembicara 3) | Arsitektur OOP `Gedung`, Topologi 63 Ruas Jalan, Fitur Rintangan Dinamis, dan **Demonstrasi Langsung Terminal CLI**. |
| **Sesi 4** | Menit 11.30 – 13.00 | **Ahmed Yasser** (Pembicara 1) | Kesimpulan Capaian UAS, Rekapitulasi Metrik, dan Penutup. |
| **Sesi 5** | Menit 13.00 – Selesai | **Seluruh Tim** | Sesi Diskusi & Tanya Jawab Dosen Penguji (Q&A). |

---

## 2. Naskah Narasi Lisan Terstruktur

### Sesi 1: Pembukaan & Latar Belakang Geospasial (Ahmed Yasser)

> **Ahmed:**  
> "Assalamu’alaikum Warahmatullahi Wabarakatuh.  
> Selamat pagi/siang kepada Bapak Dosen Pengampu mata kuliah Artificial Intelligence serta rekan-rekan mahasiswa sekalian.  
> 
> Kami dari kelompok pengembangan agen cerdas beranggotakan:  
> 1. Saya sendiri, Ahmed Yasser Luma' Nashril Ilah,  
> 2. Rekan saya, Fahmi Zaki Darmawan, dan  
> 3. Rekan saya, Muhammad Jalaluddin.  
> 
> Pada kesempatan kali ini, kami mempresentasikan dan mendemonstrasikan **Prototipe UAS** kami yang berjudul:  
> **'Rancang Bangun Agen Navigasi Cerdas Rute Antar-Gedung Kampus Menggunakan Algoritma A\* Search Berbasis Data Geospasial Riil'**.  
> 
> **Latar Belakang & Pembaruan Tahap UAS:**  
> Pada tahap UTS sebelumnya, kami memodelkan sistem dengan 12 simpul sintetis dan koordinat nominal. Namun pada **Tahap UAS** ini, sistem kami tingkatkan secara menyeluruh menjadi prototipe produksi fungsional berbasis:  
> 1. **Objek Geospasial Riil (OOP):** Mengganti simpul teks menjadi kelas `Gedung` dengan koordinat GPS asli (Latitude & Longitude) dari Google Maps untuk seluruh **36 fasilitas Kampus 1 UIN Malang**.  
> 2. **Satuan Jarak Riil Meter:** Menghitung jarak lengkung bumi menggunakan formula Haversine.  
> 3. **Topologi Pejalan Kaki Nyata:** 63 ruas jalan pedestrian yang menghubungkan seluruh fasilitas kampus.  
> 4. **Rintangan Dinamis:** Kemampuan menutup dan membuka jalan sementara secara adaptif.  
> 
> **Integritas & Data Cleansing:**  
> Sumber data mentah kami ekstrak langsung dari berkas `data_gedung.xlsx` tanpa ketergantungan library eksternal `openpyxl`. Kami berhasil menuntaskan data cleansing pada 2 anomali koordinat krusial:  
> * **Fakultas Ekonomi (ID 22):** Nilai Longitude mentah tertulis `'11.2.606784'` (typo titik ganda) berhasil dibersihkan menjadi `112.606784`.  
> * **Mabna Al-Ghozali (ID 9):** Nilai Latitude mentah tertulis `-7.94048` (salah ketik berjarak 1 km dari kampus) berhasil diselaraskan menjadi `-7.949048` pada gugus Ma'had Putra.  
> 
> Selanjutnya, landasan matematis dan teori AI akan dipaparkan oleh rekan saya, Fahmi Zaki Darmawan."

---

### Sesi 2: Teori AI, Formula Haversine, & Komparasi Algoritma (Fahmi Zaki)

> **Fahmi:**  
> "Terima kasih, Saudara Yasser.  
> Saya akan memaparkan landasan teoretis kecerdasan buatan dan formulasi matematis yang mendasari agen navigasi ini.  
> 
> **1. Formula Jarak Haversine:**  
> Agen kami menghitung jarak lengkung bumi garis lurus antar-koordinat GPS dengan radius bumi $R = 6.371.000$ meter:  
> $$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)$$  
> $$c = 2 \cdot \text{atan2}(\sqrt{a}, \sqrt{1-a}), \quad d = R \cdot c$$  
> Formula ini memberikan jarak fisik dalam satuan **meter riil**.  
> 
> **2. Pembuktian Admissibility & Consistency Heuristik $h(n)$:**  
> Pada algoritma A*, fungsi evaluasi adalah $f(n) = g(n) + h(n)$.  
> * **Admissible:** Karena jarak lengkung bumi adalah batas bawah mutlak (*geodesic lower bound*) dari setiap jalan kaki pejalan kaki yang melintasi kontur dan kelokan kampus, dan bobot jalan riil memenuhi $w(u, v) \ge \text{Haversine}(u, v)$ (dengan faktor kelokan pedestrian 10%), maka $h(n) \le h^*(n)$ **terbukti 100% Admissible**.  
> * **Consistent (Monotonic):** Berdasarkan ketidaksamaan segitiga bola (*Spherical Triangle Inequality*), berlaku $h(u) \le w(u, v) + h(v)$. Sifat konsisten ini menjamin bahwa nilai $f(n)$ tidak pernah menurun monoton di sepanjang jalur, dan simpul yang ditarik dari antrean prioritas dijamin sudah memiliki biaya optimal tanpa perlu evaluasi ulang (*no re-opening*).  
> 
> **3. Komparasi Tiga Algoritma (A* vs UCS vs BFS):**  
> * **A\* Search (Informed):** Mengarahkan pencarian langsung ke simpul tujuan dengan bantuan heuristik $h(n)$, memangkas drastis simpul yang diekspansi.  
> * **Uniform-Cost Search (UCS / Dijkstra):** Uninformed search berbasis biaya lintasan $g(n)$, digunakan sebagai acuan baku (*ground truth*) pembuktian optimalitas biaya A*.  
> * **Breadth-First Search (BFS):** Hanya meminimalkan jumlah langkah (*hop count*). Secara empiris, kami membuktikan bahwa BFS menghasilkan jarak meter yang **suboptimal pada 49.8% pasangan rute**.  
> 
> Penjelasan arsitektur kode dan demonstrasi sistem akan dilanjutkan oleh rekan saya, Muhammad Jalaluddin."

---

### Sesi 3: Metodologi Kode, Fitur Dinamis, & Demonstrasi CLI (Muhammad Jalaluddin)

> **Jalal:**  
> "Terima kasih, Saudara Fahmi.  
> Saya akan menjelaskan arsitektur perangkat lunak dan mendemonstrasikan eksekusi prototipe secara langsung.  
> 
> **Arsitektur Modular Prototipe UAS:**  
> Sistem dibangun secara modular dan berstandar *clean code*:  
> 1. `gedung.py`: Mengimplementasikan entitas OOP `Gedung` dengan *type safety*, pencegahan injeksi boolean pada koordinat, dan parser Excel mandiri.  
> 2. `campus_network.py`: Mengelola graf 36 fasilitas dan 63 ruas jalan. Menyediakan method `tutup_jalan(u, v)` dan `buka_jalan(u, v)` untuk simulasi rintangan dinamis (*Dynamic Obstacle*).  
> 3. `search_engine.py`: Mengimplementasikan A*, UCS, dan BFS menggunakan Min-Heap `heapq` dengan *tie-breaking* deterministik $O(1)$ (`tie_counter`) dan penyaringan entri usang (*lazy deletion*).  
> 4. `visualize_campus.py`: Merender peta spasial 2D beresolusi tinggi menggunakan `matplotlib` dengan koordinat bujur timur dan lintang selatan.  
> 
> **Suite Pengujian Otomatis:**  
> Kami telah membangun 25 unit test komprehensif pada `test_campus_network.py` yang mencakup integritas gedung, keterhubungan graf, admissibility, dan pengujian menyeluruh All-Pairs 1.260 pasangan. Seluruh 25 tes lulus **100% dalam 0.27 detik**.  
> 
> Sekarang, mari kita saksikan eksekusi langsung prototipe program pada antarmuka terminal."

*(Jalal berpindah ke terminal PowerShell dan mengetikkan perintah-perintah berikut satu per satu)*

#### Aksi 1: Menjalankan Demonstrasi Lengkap Prototipe UAS
```powershell
python algorithm_project/main_uas_demo.py
```
> **Penjelasan Lisan Jalal saat Output Muncul:**  
> "Perhatikan output terminal:  
> * Pertama, graf memvalidasi 36 fasilitas dan 63 ruas jalan dengan total panjang 4.445 meter, terhubung utuh dalam 1 komponen utama BFS.  
> * Pada **Skenario 1 (Jarak Dekat: Farobi ke Kantin)**: A* dan UCS menghasilkan jarak identik 115.6 meter, namun A* menghemat 33.3% ekspansi simpul.  
> * Pada **Skenario 2 (Jarak Menengah: Satpam ke Saintek)**: Jarak 186.2 meter, A* menghemat 61.5% ekspansi simpul (hanya mengekspansi 5 simpul vs 13 pada UCS).  
> * Pada **Skenario 3 (Jarak Jauh Lintas Kampus: Farobi ke Sport Center)**: Jarak A* dan UCS adalah 655.7 meter. Di sini kita melihat bukti empiris kelemahan BFS: rute BFS menempuh 720.7 meter—**65 meter lebih panjang** dari A* karena BFS hanya mengejar jumlah ruas terkecil (10 ruas vs 11 ruas pada A*).  
> * Bagian paling menarik adalah **Simulasi Rintangan Dinamis**: Ruas jalan langsung Masjid Tarbiyah ke Fak. Saintek (86.9 m) ditutup sementara. Agen A* secara otomatis mendeteksi blokade dan memutar lewat Menara UIN Malang (96.3 m). Ketika jalan dibuka kembali, rute otomatis pulih ke jalur tercepat 86.9 meter."

#### Aksi 2: Menjalankan Verifikasi Menyeluruh All-Pairs (1.260 Rute)
```powershell
python algorithm_project/main_uas_demo.py --verify-all
```
> **Penjelasan Lisan Jalal:**  
> "Perintah ini menguji seluruh 1.260 pasangan gedung di Kampus 1 UIN Malang.  
> Hasilnya:  
> 1. **0 mismatch biaya** antara A* dan UCS.  
> 2. A* mengekspansi simpul lebih sedikit pada 96.5% pasangan rute, dan rata-rata menghemat **56.7% ekspansi simpul**.  
> 3. BFS terbukti suboptimal pada **49.8% rute**."

#### Aksi 3: Pencarian Rute Kustom Berdasarkan Nama Gedung
```powershell
python algorithm_project/main_uas_demo.py --start "Masjid Tarbiyah" --goal "Fakultas Saintek"
```
> **Penjelasan Lisan Jalal:**  
> "Pengguna dapat mencari rute antar-gedung apa pun dengan fleksibel menggunakan nama gedung maupun nomor ID."

---

### Sesi 4: Kesimpulan & Penutup (Ahmed Yasser)

> **Ahmed:**  
> "Terima kasih, Saudara Jalal.  
> Dari seluruh perancangan, implementasi, dan pengujian komputasional yang telah kami lakukan, dapat ditarik kesimpulan:  
> 1. Prototipe UAS telah berhasil mengintegrasikan data geospasial riil 36 fasilitas Kampus 1 UIN Malang dengan formula Haversine berjarak meter riil.  
> 2. Heuristik jarak garis lurus Haversine terbukti 100% *admissible* dan *consistent*, menghasilkan rute berbiaya minimum yang identik dengan UCS pada seluruh 1.260 pasangan rute uji (0 mismatch).  
> 3. Algoritma A* Search membuktikan keunggulannya dengan efisiensi ekspansi rata-rata 56.7% lebih hemat dibanding UCS, serta mengungguli BFS yang terbukti menghasilkan rute tidak optimal pada separuh rute kampus.  
> 4. Fitur rintangan dinamis membuktikan fleksibilitas agen dalam menangani penutupan jalan sementara secara adaptif.  
> 
> Demikian pemaparan dan demonstrasi Prototipe UAS dari kelompok kami. Kami membuka sesi tanya jawab dan siap menerima pertanyaan maupun masukan dari Bapak Dosen.  
> Wassalamu’alaikum Warahmatullahi Wabarakatuh."

---

## 3. Strategi Menjawab Pertanyaan Dosen (Q&A Strategy)

| Kategori Pertanyaan | Target Penjawab | Poin Kunci Jawaban |
|:---|:---:|:---|
| **Formula Haversine & Geodesik** | **Fahmi Zaki** | Jelaskan bahwa Haversine memperhitungkan kelengkungan bola bumi dengan radius $R = 6.371.000$ m, sehingga jarak antar-koordinat GPS akurat dalam satuan meter tanpa distorsi proyeksi datar. |
| **Pembuktian Admissibility & Consistency** | **Fahmi Zaki** | Garis lurus lengkung bumi adalah jarak terpendek mutlak pada bidang bola (geodesik). Karena jalan pejalan kaki berbelok melintasi belokan ($w \ge d$), maka $h(n) \le h^*(n)$ (Admissible). Ketidaksamaan segitiga bola menjamin $h(u) \le w(u, v) + h(v)$ (Consistent/Monotonic). |
| **Mengapa BFS Jaraknya Lebih Panjang?** | **Fahmi Zaki** | BFS adalah *uninformed search* yang mengasumsikan seluruh sisi memiliki bobot seragam (= 1 hop). Pada skenario 3, BFS memilih jalur 10 langkah yang melewati koridor panjang, sedangkan A* memilih 11 langkah tetapi tiap langkahnya berjarak pendek, sehingga total meter A* jauh lebih hemat. |
| **Arsitektur OOP `Gedung` & Data Cleansing** | **Ahmed Yasser** | Jelaskan bahwa pembacaan Excel menggunakan `zipfile` dan `xml.etree.ElementTree` mandiri tanpa `openpyxl`. Cleansing ID 22 (Fak. Ekonomi) membetulkan typo titik ganda `11.2.606784` menjadi `112.606784`, dan ID 9 (Mabna Al-Ghozali) membetulkan `-7.94048` menjadi `-7.949048`. |
| **Struktur Min-Heap & Penanganan Tie-Breaking** | **Muhammad Jalaluddin** | Jelaskan penambahan `tie_counter` inkremental unik pada tuple Min-Heap `(f, g, counter, node, path)` agar pemutus seri berjalan instan dalam $O(1)$ tanpa pernah membandingkan objek `Gedung`. Entri usang ditangani secara efisien via *lazy deletion* (`if g > cost_so_far[curr]: continue`). |
| **Mekanisme Penutupan Jalan Dinamis** | **Muhammad Jalaluddin** | Tunjukkan method `tutup_jalan(u, v)` yang memindahkan sisi aktif ke kamus `closed_edges`. Saat A* dijalankan kembali, lintasan langsung tidak lagi tersedia di tetangga simpul, memaksa agen mencari jalur memutar terbaik. Ketika `buka_jalan(u, v)` dipanggil, sisi dipulihkan ke adjacency list aktif. |
