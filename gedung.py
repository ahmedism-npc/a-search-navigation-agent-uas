"""
=============================================================================
MODUL GEOSPASIAL GEDUNG & DATA LOADER (TAHAP UAS)
Mata Kuliah : Artificial Intelligence (Semester 5 OBE)
Institusi   : Teknik Informatika, UIN Maulana Malik Ibrahim Malang
Deskripsi   : Kelas entitas Gedung berbasis OOP, formula jarak Haversine riil,
              dan parser data Excel (.xlsx) mandiri tanpa dependensi openpyxl.
=============================================================================
"""

import math
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Tuple, Any

# Konstanta Radius Bumi rata-rata (WGS-84 / IUGG) dalam meter
EARTH_RADIUS_METERS: float = 6371000.0


def hitung_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Menghitung jarak garis lurus lengkung bumi (great-circle distance)
    antara dua koordinat GPS (derajat) menggunakan formula Haversine.
    
    Formula:
        a = sin^2(delta_lat / 2) + cos(lat1) * cos(lat2) * sin^2(delta_lon / 2)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        d = R * c
        
    Parameter:
        lat1, lon1: Koordinat titik awal (derajat desimal)
        lat2, lon2: Koordinat titik tujuan (derajat desimal)
        
    Kembalian:
        Jarak garis lurus dalam satuan meter riil (float).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    
    # Menghindari galat numerik presisi floating point batas domain sqrt
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_METERS * c


class Gedung:
    """
    Entitas fasilitas/gedung kampus berbasis Object-Oriented Programming (OOP).
    
    Menyimpan atribut spasial riil (latitude, longitude) dari Google Maps,
    identitas, kategori fasilitas, serta method penghitungan jarak spasial.
    """
    def __init__(self, id_gedung: int, nama: str, latitude: float, longitude: float, kategori: str = "Umum"):
        self.id: int = int(id_gedung)
        # Standardisasi nama agar bebas dari whitespace berlebih
        self.nama: str = re.sub(r'\s+', ' ', str(nama)).strip()

        # Tolak tipe boolean (karena bool adalah subclass int di Python)
        if isinstance(latitude, bool) or isinstance(longitude, bool):
            raise TypeError(f"Koordinat tidak boleh bertipe boolean pada Gedung ID {self.id}")

        self.latitude: float = float(latitude)
        self.longitude: float = float(longitude)
        self.kategori: str = re.sub(r'\s+', ' ', str(kategori)).strip()

        # Validasi koordinat numerik finite
        if not (math.isfinite(self.latitude) and math.isfinite(self.longitude)):
            raise ValueError(f"Koordinat non-finite pada Gedung ID {self.id}: ({self.latitude}, {self.longitude})")

    def jarak_ke(self, other: 'Gedung') -> float:
        """
        Menghitung jarak garis lurus Haversine dari gedung ini ke gedung lain dalam meter riil.
        Fungsi ini menjadi landasan fungsi heuristik h(n) A* Search.
        """
        if not isinstance(other, Gedung):
            raise TypeError(f"Argumen harus bertipe Gedung, bukan {type(other).__name__}")
        if self.id == other.id:
            return 0.0
        return hitung_haversine(self.latitude, self.longitude, other.latitude, other.longitude)

    def to_dict(self) -> Dict[str, Any]:
        """Konversi objek Gedung ke representasi dictionary."""
        return {
            "id": self.id,
            "nama": self.nama,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "kategori": self.kategori
        }

    def __repr__(self) -> str:
        return f"Gedung(id={self.id}, nama='{self.nama}', lat={self.latitude:.6f}, lon={self.longitude:.6f}, kategori='{self.kategori}')"

    def __str__(self) -> str:
        return f"[{self.id:02d}] {self.nama} ({self.kategori})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Gedung):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __lt__(self, other: object) -> bool:
        """Dibutuhkan untuk penanganan tie-breaking deterministik pada Min-Heap antrean prioritas."""
        if not isinstance(other, Gedung):
            return NotImplemented
        return self.id < other.id


# Pemetaan kategori fasilitas Kampus 1 UIN Malang
KATEGORI_MAPPING: Dict[int, str] = {
    1: "Ma'had Putra",       # Mabna Farobi
    2: "Ma'had Putra",       # Mabna Ibn Khaldun
    3: "Ma'had Putra",       # Mabna Muhasibi
    4: "Kantin & Logistik",  # Kantin Al-Kautsar
    5: "Ibadah & Majelis",   # Halaqoh
    6: "Administrasi Ma'had",# Kantor Pusat Ma'had
    7: "Ma'had Putra",       # Mabna Ibn Sina
    8: "Ma'had Putra",       # Mabna Ibn Rusydi
    9: "Ma'had Putra",       # Mabna Al-Ghozali
    10: "Keamanan Ma'had",   # Kantor Satpam Mahad
    11: "Layanan Umum",      # Sanggar Printing UIN Malang
    12: "Asrama Takmir",     # Asrama Takmir
    13: "Masjid Kampus",     # Masjid Tarbiyah
    14: "Akademik",          # Gedung Micro Teaching
    15: "Fakultas",          # Fakultas Humaniora
    16: "Layanan Kampus",    # Pusat Informasi UIN Maliki
    17: "Landmark Kampus",   # Menara UIN Malang
    18: "Fakultas",          # Fakultas Saintek
    19: "Perpustakaan",      # Perpustakaan Pusat
    20: "Rektorat & Biro",   # Rektorat
    21: "Media & Informasi", # Simfoni FM Malang
    22: "Fakultas",          # Fakultas Ekonomi
    23: "Fakultas",          # Fakultas Syariah
    24: "Fakultas",          # Fakultas Tarbiyah
    25: "Gedung Kuliah",     # Gedung B
    26: "Gedung Kuliah",     # Gedung C
    27: "Sarana Olahraga",   # Lapangan Utama
    28: "Sarana Olahraga",   # Lapangan Basket
    29: "Sarana Olahraga",   # Gedung SC
    30: "Masjid Kampus",     # Masjid Ulul Albab
    31: "Ma'had Putri",      # Mabna Ummu Salamah
    32: "Ma'had Putri",      # Mabna Asma' Binti Abu Bakar
    33: "Ma'had Putri",      # Mabna Fatimah Az-Zahra
    34: "Ma'had Putri",      # Mabna Khadijah Al-Kubra
    35: "Layanan Kesehatan", # Poliklinik
    36: "Gedung Kuliah",     # Gedung D
}

# Standardisasi nama gedung resmi (Title Case & perbaikan typo)
NAMA_STANDARDIZATION: Dict[int, str] = {
    1: "Mabna Farobi",
    2: "Mabna Ibn Khaldun",
    3: "Mabna Muhasibi",
    4: "Kantin Al-Kautsar",
    5: "Halaqoh",
    6: "Kantor Pusat Ma'had",
    7: "Mabna Ibn Sina",
    8: "Mabna Ibn Rusydi",
    9: "Mabna Al-Ghozali",
    10: "Pos Satpam Ma'had",
    11: "Sanggar Printing UIN Malang",
    12: "Asrama Takmir",
    13: "Masjid Tarbiyah",
    14: "Gedung Micro Teaching",
    15: "Fakultas Humaniora",
    16: "Pusat Informasi UIN Maliki",
    17: "Menara UIN Malang",
    18: "Fakultas Saintek",
    19: "Perpustakaan Pusat",
    20: "Gedung Rektorat",
    21: "Simfoni FM Malang",
    22: "Fakultas Ekonomi",
    23: "Fakultas Syariah",
    24: "Fakultas Tarbiyah",
    25: "Gedung Perkuliahan B",
    26: "Gedung Perkuliahan C",
    27: "Lapangan Utama",
    28: "Lapangan Basket",
    29: "Gedung SC (Sport Center)",
    30: "Masjid Ulul Albab",
    31: "Mabna Ummu Salamah",
    32: "Mabna Asma' Binti Abu Bakar",
    33: "Mabna Fatimah Az-Zahra",
    34: "Mabna Khadijah Al-Kubra",
    35: "Poliklinik Kampus",
    36: "Gedung Perkuliahan D",
}


def load_gedung_from_excel(filepath: str) -> Dict[int, Gedung]:
    """
    Mengekstrak dan membersihkan seluruh 36 data fasilitas dari berkas data_gedung.xlsx
    menggunakan pustaka standar Python (zipfile + xml.etree.ElementTree).
    
    Aturan Data Cleansing Wajib:
    1. Fakultas Ekonomi (ID 22): Nilai Longitude '11.2.606784' diperbaiki menjadi 112.606784.
    2. Mabna Al-Ghozali (ID 9): Nilai Latitude -7.94048 diperbaiki menjadi -7.949048.
    3. Standardisasi nama gedung (Title Case rapi, perbaikan spasi, penamaan konsisten).
    4. Pengelompokan kategori fasilitas kampus.
    
    Parameter:
        filepath: Jalur file data_gedung.xlsx
        
    Kembalian:
        Dictionary pemetaan ID gedung (int) ke objek Gedung.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Berkas data gedung tidak ditemukan pada: {filepath}")

    with zipfile.ZipFile(filepath, 'r') as zf:
        # 1. Baca shared strings
        shared_strings = []
        if 'xl/sharedStrings.xml' in zf.namelist():
            ss_tree = ET.fromstring(zf.read('xl/sharedStrings.xml'))
            ns_ss = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for elem in ss_tree.findall('ns:si', ns_ss):
                # Teks dapat berada langsung di <t> atau tersebar di elemen anak <r><t>
                text_parts = [t.text for t in elem.findall('.//ns:t', ns_ss) if t.text]
                shared_strings.append(''.join(text_parts))

        # 2. Baca lembar sheet1.xml
        sheet_tree = ET.fromstring(zf.read('xl/worksheets/sheet1.xml'))
        ns_sheet = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        rows = sheet_tree.findall('.//ns:row', ns_sheet)

        gedung_dict: Dict[int, Gedung] = {}

        for row in rows:
            col_data: Dict[str, str] = {}
            for cell in row.findall('ns:c', ns_sheet):
                cell_ref = cell.attrib.get('r', '')
                col_letter = ''.join([c for c in cell_ref if c.isalpha()])
                cell_type = cell.attrib.get('t', '')
                val_elem = cell.find('ns:v', ns_sheet)
                cell_val = val_elem.text if val_elem is not None else ''

                if cell_type == 's' and cell_val:
                    cell_val = shared_strings[int(cell_val)]

                col_data[col_letter] = cell_val.strip()

            # Kolom B = ID, C = Nama Gedung, D = Latitude, E = Longitude
            col_b = col_data.get('B', '')
            if col_b and col_b.isdigit():
                gid = int(col_b)
                raw_name = col_data.get('C', '')
                raw_lat = col_data.get('D', '')
                raw_lon = col_data.get('E', '')

                # -------------------------------------------------------------
                # DATA CLEANSING ATURAN 1: Fakultas Ekonomi (ID 22) Longitude
                # -------------------------------------------------------------
                if gid == 22 and ('11.2.' in raw_lon or raw_lon == '11.2.606784'):
                    lon = 112.606784
                else:
                    try:
                        lon = float(raw_lon)
                    except ValueError:
                        # Penanganan fallback jika ada typo pemisah titik ganda
                        cleaned_lon = raw_lon.replace('..', '.').replace('11.2.', '112.')
                        lon = float(cleaned_lon)

                # -------------------------------------------------------------
                # DATA CLEANSING ATURAN 2: Mabna Al-Ghozali (ID 9) Latitude
                # -------------------------------------------------------------
                try:
                    lat_parsed = float(raw_lat)
                except ValueError:
                    lat_parsed = float(raw_lat.replace('..', '.'))

                if gid == 9 and abs(lat_parsed - (-7.94048)) < 1e-4:
                    lat = -7.949048
                else:
                    lat = lat_parsed

                # -------------------------------------------------------------
                # DATA CLEANSING ATURAN 3: Standardisasi Nama & Kategori
                # -------------------------------------------------------------
                cleaned_raw_title = re.sub(r'\s+', ' ', raw_name).strip().title()
                nama_gedung = NAMA_STANDARDIZATION.get(gid, cleaned_raw_title)
                kategori = KATEGORI_MAPPING.get(gid, "Fasilitas Kampus")

                obj_gedung = Gedung(
                    id_gedung=gid,
                    nama=nama_gedung,
                    latitude=lat,
                    longitude=lon,
                    kategori=kategori
                )
                gedung_dict[gid] = obj_gedung

    if len(gedung_dict) != 36:
        raise ValueError(f"Ekstraksi data tidak lengkap: diharapkan 36 gedung, ditemukan {len(gedung_dict)}")

    return gedung_dict


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(current_dir, "data_gedung.xlsx")
    print(f"Mengekstrak data dari: {excel_path}")
    daftar_gedung = load_gedung_from_excel(excel_path)
    print(f"Berhasil memuat {len(daftar_gedung)} objek Gedung!")
    print("-" * 75)
    print(f"{'ID':<4} {'Kategori':<20} {'Nama Gedung':<30} {'Latitude':<12} {'Longitude':<12}")
    print("-" * 75)
    for gid in sorted(daftar_gedung.keys()):
        g = daftar_gedung[gid]
        print(f"{g.id:<4} {g.kategori:<20} {g.nama:<30} {g.latitude:<12.6f} {g.longitude:<12.6f}")
    print("-" * 75)
    
    # Uji jarak sampel
    g1 = daftar_gedung[1]   # Mabna Farobi
    g4 = daftar_gedung[4]   # Kantin Al-Kautsar
    g29 = daftar_gedung[29] # Gedung SC
    print(f"Jarak garis lurus Haversine:")
    print(f"  {g1.nama} -> {g4.nama} : {g1.jarak_ke(g4):.2f} meter")
    print(f"  {g1.nama} -> {g29.nama}: {g1.jarak_ke(g29):.2f} meter")
