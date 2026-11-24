"""
=============================================================================
JARINGAN JALAN KAMPUS (CAMPUS GRAPH NETWORK) - TAHAP UAS
Mata Kuliah : Artificial Intelligence (Semester 5 OBE)
Institusi   : Teknik Informatika, UIN Maulana Malik Ibrahim Malang
Deskripsi   : Representasi graf berbobot tidak berarah menghubungkan 36 fasilitas
              Kampus 1 UIN Malang dengan topologi pejalan kaki riil, verifikasi
              konektivitas, dan simulasi penutupan jalan dinamis (Dynamic Obstacle).
=============================================================================
"""

import os
import sys
from collections import deque
from typing import Dict, List, Tuple, Set, Optional, Union, Any

# Tambahkan direktori modul ke sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from gedung import Gedung, load_gedung_from_excel

# Daftar 63 ruas jalan pedestrian & aspal Kampus 1 UIN Malang
# Menghubungkan seluruh 36 fasilitas kampus secara logis dan realistis
DEFAULT_CAMPUS_EDGES: List[Tuple[int, int]] = [
    # -------------------------------------------------------------------------
    # Cluster 1: Ma'had Putra (Utara)
    # -------------------------------------------------------------------------
    (1, 2),   # Mabna Farobi <-> Mabna Ibn Khaldun
    (1, 3),   # Mabna Farobi <-> Mabna Muhasibi
    (2, 3),   # Mabna Ibn Khaldun <-> Mabna Muhasibi
    (2, 4),   # Mabna Ibn Khaldun <-> Kantin Al-Kautsar
    (3, 7),   # Mabna Muhasibi <-> Mabna Ibn Sina
    (4, 5),   # Kantin Al-Kautsar <-> Halaqoh
    (4, 7),   # Kantin Al-Kautsar <-> Mabna Ibn Sina
    (5, 6),   # Halaqoh <-> Kantor Pusat Ma'had
    (6, 8),   # Kantor Pusat Ma'had <-> Mabna Ibn Rusydi
    (6, 10),  # Kantor Pusat Ma'had <-> Pos Satpam Ma'had
    (7, 9),   # Mabna Ibn Sina <-> Mabna Al-Ghozali
    (8, 9),   # Mabna Ibn Rusydi <-> Mabna Al-Ghozali
    (8, 10),  # Mabna Ibn Rusydi <-> Pos Satpam Ma'had
    (9, 12),  # Mabna Al-Ghozali <-> Asrama Takmir
    (10, 11), # Pos Satpam Ma'had <-> Sanggar Printing UIN Malang
    (11, 12), # Sanggar Printing UIN Malang <-> Asrama Takmir
    (12, 13), # Asrama Takmir <-> Masjid Tarbiyah
    (12, 17), # Asrama Takmir <-> Menara UIN Malang
    
    # -------------------------------------------------------------------------
    # Cluster 2: Koridor Tengah, Boulevard Rektorat & Saintek
    # -------------------------------------------------------------------------
    (13, 14), # Masjid Tarbiyah <-> Gedung Micro Teaching
    (13, 17), # Masjid Tarbiyah <-> Menara UIN Malang
    (13, 18), # Masjid Tarbiyah <-> Fakultas Saintek
    (14, 15), # Gedung Micro Teaching <-> Fakultas Humaniora
    (14, 19), # Gedung Micro Teaching <-> Perpustakaan Pusat
    (15, 16), # Fakultas Humaniora <-> Pusat Informasi UIN Maliki
    (15, 20), # Fakultas Humaniora <-> Gedung Rektorat
    (16, 20), # Pusat Informasi UIN Maliki <-> Gedung Rektorat
    (17, 18), # Menara UIN Malang <-> Fakultas Saintek
    (17, 21), # Menara UIN Malang <-> Simfoni FM Malang
    (18, 19), # Fakultas Saintek <-> Perpustakaan Pusat
    (18, 21), # Fakultas Saintek <-> Simfoni FM Malang
    (18, 22), # Fakultas Saintek <-> Fakultas Ekonomi
    (18, 24), # Fakultas Saintek <-> Fakultas Tarbiyah
    (19, 20), # Perpustakaan Pusat <-> Gedung Rektorat
    (19, 24), # Perpustakaan Pusat <-> Fakultas Tarbiyah
    (20, 35), # Gedung Rektorat <-> Poliklinik Kampus
    (21, 22), # Simfoni FM Malang <-> Fakultas Ekonomi
    
    # -------------------------------------------------------------------------
    # Cluster 3: Fakultas Selatan, Lapangan & Gedung Kuliah
    # -------------------------------------------------------------------------
    (22, 23), # Fakultas Ekonomi <-> Fakultas Syariah
    (22, 24), # Fakultas Ekonomi <-> Fakultas Tarbiyah
    (23, 24), # Fakultas Syariah <-> Fakultas Tarbiyah
    (23, 26), # Fakultas Syariah <-> Gedung Perkuliahan C
    (23, 27), # Fakultas Syariah <-> Lapangan Utama
    (24, 25), # Fakultas Tarbiyah <-> Gedung Perkuliahan B
    (24, 35), # Fakultas Tarbiyah <-> Poliklinik Kampus
    (25, 27), # Gedung Perkuliahan B <-> Lapangan Utama
    (25, 30), # Gedung Perkuliahan B <-> Masjid Ulul Albab
    (25, 35), # Gedung Perkuliahan B <-> Poliklinik Kampus
    (26, 27), # Gedung Perkuliahan C <-> Lapangan Utama
    (26, 28), # Gedung Perkuliahan C <-> Lapangan Basket
    (26, 36), # Gedung Perkuliahan C <-> Gedung Perkuliahan D
    (27, 28), # Lapangan Utama <-> Lapangan Basket
    
    # -------------------------------------------------------------------------
    # Cluster 4: Ma'had Putri, Sport Center & Area Barat
    # -------------------------------------------------------------------------
    (28, 29), # Lapangan Basket <-> Gedung SC (Sport Center)
    (28, 30), # Lapangan Basket <-> Masjid Ulul Albab
    (28, 31), # Lapangan Basket <-> Mabna Ummu Salamah
    (29, 30), # Gedung SC (Sport Center) <-> Masjid Ulul Albab
    (29, 34), # Gedung SC (Sport Center) <-> Mabna Khadijah Al-Kubra
    (29, 36), # Gedung SC (Sport Center) <-> Gedung Perkuliahan D
    (30, 31), # Masjid Ulul Albab <-> Mabna Ummu Salamah
    (31, 33), # Mabna Ummu Salamah <-> Mabna Fatimah Az-Zahra
    (31, 34), # Mabna Ummu Salamah <-> Mabna Khadijah Al-Kubra
    (32, 33), # Mabna Asma' Binti Abu Bakar <-> Mabna Fatimah Az-Zahra
    (32, 34), # Mabna Asma' Binti Abu Bakar <-> Mabna Khadijah Al-Kubra
    (33, 34), # Mabna Fatimah Az-Zahra <-> Mabna Khadijah Al-Kubra
    (34, 36), # Mabna Khadijah Al-Kubra <-> Gedung Perkuliahan D
]


class CampusGraph:
    """
    Representasi Graf Jaringan Jalan Kampus berbasis Objek Gedung.
    
    Fitur Utama:
    - Adjacency list berbasis objek Gedung: adj[u][v] = bobot_meter.
    - Bobot sisi menjamin w(u, v) >= Haversine(u, v) (Admissibility Heuristik).
    - Verifikasi konektivitas graf menyeluruh via BFS.
    - Mekanisme penutupan jalan dinamis (tutup_jalan dan buka_jalan) untuk simulasi UAS.
    """
    def __init__(self, gedung_dict: Dict[int, Gedung], raw_edges: Optional[List[Tuple[int, int]]] = None):
        self.gedung_dict: Dict[int, Gedung] = dict(gedung_dict)
        
        # Adjacency list: Gedung -> Dict[Gedung, float]
        self.adj: Dict[Gedung, Dict[Gedung, float]] = {g: {} for g in self.gedung_dict.values()}
        
        # Catatan sisi jalan aktif dan sisi jalan yang ditutup sementara
        # Tuple diseragamkan (min_id, max_id) untuk sisi tidak berarah
        self.active_edges: Set[Tuple[int, int]] = set()
        self.closed_edges: Dict[Tuple[int, int], float] = {}

        edges_to_build = raw_edges if raw_edges is not None else DEFAULT_CAMPUS_EDGES
        self._build_network(edges_to_build)

    def _build_network(self, edges: List[Tuple[int, int]]) -> None:
        """Membangun topologi graf dengan bobot sisi jalan pejalan kaki realistis."""
        for u_id, v_id in edges:
            if u_id not in self.gedung_dict:
                raise ValueError(f"Gedung ID {u_id} tidak ditemukan dalam basis data!")
            if v_id not in self.gedung_dict:
                raise ValueError(f"Gedung ID {v_id} tidak ditemukan dalam basis data!")
            if u_id == v_id:
                raise ValueError(f"Self-loop terdeteksi pada Gedung ID {u_id}!")

            edge_key = (min(u_id, v_id), max(u_id, v_id))
            if edge_key in self.active_edges:
                continue

            g_u = self.gedung_dict[u_id]
            g_v = self.gedung_dict[v_id]

            # Jarak Haversine garis lurus
            d_hav = g_u.jarak_ke(g_v)
            
            # Bobot sisi jalan pejalan kaki riil: Haversine * faktor kelokan pedestrian (1.10)
            # Menjamin strictly w(u, v) >= d_hav (Admissible dan Consistent)
            bobot_riil = round(d_hav * 1.10, 1)

            self.adj[g_u][g_v] = bobot_riil
            self.adj[g_v][g_u] = bobot_riil
            self.active_edges.add(edge_key)

    def get_gedung(self, identifier: Union[int, str, Gedung]) -> Optional[Gedung]:
        """Mencari objek Gedung berdasarkan ID (int), Nama (str), atau referensi Gedung."""
        if isinstance(identifier, Gedung):
            return identifier if identifier.id in self.gedung_dict else None
        if isinstance(identifier, int):
            return self.gedung_dict.get(identifier)
        if isinstance(identifier, str):
            clean_str = identifier.strip().lower()
            # Coba konversi ke int jika teks numerik
            if clean_str.isdigit():
                return self.gedung_dict.get(int(clean_str))
            # Lintasan 1: Prioritaskan exact match nama gedung
            for g in self.gedung_dict.values():
                if g.nama.lower() == clean_str:
                    return g
            # Lintasan 2: Fallback ke substring match jika tidak ada exact match
            for g in self.gedung_dict.values():
                if clean_str in g.nama.lower():
                    return g
        return None

    def get_neighbors(self, gedung: Gedung) -> Dict[Gedung, float]:
        """Mengembalikan kamus tetangga aktif beserta bobot jaraknya (meter)."""
        return self.adj.get(gedung, {})

    def tutup_jalan(self, u: Union[int, str, Gedung], v: Union[int, str, Gedung]) -> bool:
        """
        Menutup ruas jalan sementara antara gedung u dan v (Simulasi Rintangan Dinamis).
        Menghapus sisi dari adjacency list aktif dan menyimpannya di closed_edges.
        """
        g_u = self.get_gedung(u)
        g_v = self.get_gedung(v)

        if not g_u or not g_v:
            raise ValueError(f"Simpul tidak valid: {u} atau {v}")

        edge_key = (min(g_u.id, g_v.id), max(g_u.id, g_v.id))
        if edge_key not in self.active_edges:
            return False  # Sisi memang tidak aktif / tidak ada

        bobot = self.adj[g_u][g_v]
        del self.adj[g_u][g_v]
        del self.adj[g_v][g_u]

        self.active_edges.remove(edge_key)
        self.closed_edges[edge_key] = bobot
        return True

    def buka_jalan(self, u: Union[int, str, Gedung], v: Union[int, str, Gedung], bobot: Optional[float] = None) -> bool:
        """
        Membuka kembali ruas jalan yang sebelumnya ditutup.
        Mengembalikan sisi ke adjacency list aktif.
        """
        g_u = self.get_gedung(u)
        g_v = self.get_gedung(v)

        if not g_u or not g_v:
            raise ValueError(f"Simpul tidak valid: {u} atau {v}")

        edge_key = (min(g_u.id, g_v.id), max(g_u.id, g_v.id))
        
        if edge_key in self.active_edges:
            return False  # Sisi sudah aktif

        if bobot is None:
            if edge_key in self.closed_edges:
                bobot = self.closed_edges.pop(edge_key)
            else:
                return False  # Sisi tidak sedang dalam daftar ditutup (mencegah penambahan sisi liar)
        else:
            self.closed_edges.pop(edge_key, None)

        self.adj[g_u][g_v] = bobot
        self.adj[g_v][g_u] = bobot
        self.active_edges.add(edge_key)
        return True

    def is_connected(self) -> bool:
        """
        Memeriksa apakah seluruh 36 gedung terhubung dalam satu komponen utama
        menggunakan penelusuran Breadth-First Search (BFS).
        """
        if not self.gedung_dict:
            return False
            
        start_node = next(iter(self.gedung_dict.values()))
        visited: Set[Gedung] = {start_node}
        queue: deque = deque([start_node])

        while queue:
            curr = queue.popleft()
            for neighbor in self.adj.get(curr, {}):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return len(visited) == len(self.gedung_dict)

    def get_connected_components(self) -> List[Set[Gedung]]:
        """Mengembalikan daftar komponen terhubung pada graf."""
        visited: Set[Gedung] = set()
        components: List[Set[Gedung]] = []

        for node in self.gedung_dict.values():
            if node not in visited:
                comp: Set[Gedung] = {node}
                visited.add(node)
                queue: deque = deque([node])
                while queue:
                    curr = queue.popleft()
                    for neighbor in self.adj.get(curr, {}):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            comp.add(neighbor)
                            queue.append(neighbor)
                components.append(comp)
        return components

    def get_total_network_length(self) -> float:
        """Menghitung total panjang seluruh ruas jalan kampus aktif (dalam meter)."""
        total = 0.0
        for (u_id, v_id) in self.active_edges:
            g_u = self.gedung_dict[u_id]
            g_v = self.gedung_dict[v_id]
            total += self.adj[g_u][g_v]
        return round(total, 1)

    def summary(self) -> Dict[str, Any]:
        """Ringkasan statistik jaringan kampus."""
        return {
            "total_gedung": len(self.gedung_dict),
            "total_ruas_aktif": len(self.active_edges),
            "total_ruas_ditutup": len(self.closed_edges),
            "total_panjang_jalan_meter": self.get_total_network_length(),
            "terhubung": self.is_connected()
        }


def create_default_campus_graph(excel_path: Optional[str] = None) -> CampusGraph:
    """Fungsi pembantu instansiasi graf standar Kampus 1 UIN Malang."""
    if excel_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        excel_path = os.path.join(current_dir, "data_gedung.xlsx")
    gedung_dict = load_gedung_from_excel(excel_path)
    return CampusGraph(gedung_dict, DEFAULT_CAMPUS_EDGES)


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(current_dir, "data_gedung.xlsx")
    
    graph = create_default_campus_graph(excel_file)
    stat = graph.summary()
    
    print("=" * 65)
    print("  STATISTIK JARINGAN JALAN KAMPUS 1 UIN MALANG (CAMPUS GRAPH)")
    print("=" * 65)
    print(f"Total Gedung / Fasilitas : {stat['total_gedung']} gedung")
    print(f"Total Ruas Jalan Aktif   : {stat['total_ruas_aktif']} ruas jalan")
    print(f"Total Panjang Jaringan   : {stat['total_panjang_jalan_meter']:.1f} meter ({stat['total_panjang_jalan_meter']/1000:.2f} km)")
    print(f"Status Keterhubungan Graf: {'TERHUBUNG (1 Komponen Utama)' if stat['terhubung'] else 'TERPUTUS'}")
    print("-" * 65)
    
    # Uji simulasi penutupan jalan
    g13 = graph.get_gedung(13) # Masjid Tarbiyah
    g18 = graph.get_gedung(18) # Fak. Saintek
    print(f"Uji Penutupan Jalan: {g13.nama} <-> {g18.nama}")
    sukses_tutup = graph.tutup_jalan(g13, g18)
    print(f"  Penutupan jalan berhasil: {sukses_tutup}")
    print(f"  Ruas aktif tersisa: {len(graph.active_edges)}, Ditutup: {len(graph.closed_edges)}")
    print(f"  Apakah graf tetap terhubung melalui jalur alternatif? {graph.is_connected()}")
    
    # Buka kembali
    graph.buka_jalan(g13, g18)
    print(f"  Jalan dibuka kembali. Ruas aktif: {len(graph.active_edges)}")
    print("=" * 65)
