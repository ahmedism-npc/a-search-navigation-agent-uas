"""
=============================================================================
SUITE PENGUJIAN REGRESI & UNIT TEST - TAHAP UAS MINI PROJECT AI
Mata Kuliah : Artificial Intelligence (Semester 5 OBE)
Institusi   : Teknik Informatika, UIN Maulana Malik Ibrahim Malang
Deskripsi   : Pengujian otomatis integritas 36 objek Gedung, data cleansing,
              konektivitas graf, admissibility heuristik Haversine, optimalitas
              A* vs UCS (1.260 pasangan), dan penutupan jalan dinamis.
=============================================================================
"""

import os
import sys
import math
import unittest
from typing import Dict, List, Set, Tuple

# Tambahkan direktori modul ke sys.path agar dapat dieksekusi dari mana saja
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from gedung import Gedung, hitung_haversine, load_gedung_from_excel
from campus_network import CampusGraph, create_default_campus_graph, DEFAULT_CAMPUS_EDGES
from search_engine import (
    astar_search,
    ucs_search,
    bfs_search,
    compare_algorithms,
    verify_all_pairs
)


class TestCampusNetworkUAS(unittest.TestCase):
    """Suite pengujian komprehensif implementasi tahap UAS."""

    @classmethod
    def setUpClass(cls):
        """Inisialisasi graf standar kampus sekali sebelum seluruh pengujian dijalankan."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cls.excel_path = os.path.join(current_dir, "data_gedung.xlsx")
        cls.graph = create_default_campus_graph(cls.excel_path)
        cls.gedung_dict = cls.graph.gedung_dict

    # =========================================================================
    # 1. VALIDASI ENTITAS GEDUNG & DATA CLEANSING DARI EXCEL
    # =========================================================================
    def test_total_gedung_count(self):
        """Memastikan tepat 36 fasilitas Kampus 1 UIN Malang berhasil diekstrak."""
        self.assertEqual(len(self.gedung_dict), 36)
        expected_ids = set(range(1, 37))
        self.assertEqual(set(self.gedung_dict.keys()), expected_ids)

    def test_data_cleansing_fakultas_ekonomi_longitude(self):
        """
        Validasi Cleansing 1:
        Fakultas Ekonomi (ID 22) dengan typo '11.2.606784' wajib bersih menjadi 112.606784.
        """
        g22 = self.gedung_dict[22]
        self.assertEqual(g22.nama, "Fakultas Ekonomi")
        self.assertAlmostEqual(g22.longitude, 112.606784, places=6)
        self.assertAlmostEqual(g22.latitude, -7.951459, places=6)

    def test_data_cleansing_mabna_al_ghozali_latitude(self):
        """
        Validasi Cleansing 2:
        Mabna Al-Ghozali (ID 9) dengan typo -7.94048 (berjarak 1 km) wajib diselaraskan
        menjadi -7.949048 pada gugus Ma'had Putra.
        """
        g9 = self.gedung_dict[9]
        self.assertEqual(g9.nama, "Mabna Al-Ghozali")
        self.assertAlmostEqual(g9.latitude, -7.949048, places=6)
        self.assertAlmostEqual(g9.longitude, 112.606614, places=6)

    def test_coordinates_are_finite_and_in_malang_region(self):
        """Memastikan semua koordinat berhingga dan berada di wilayah Kampus 1 Malang (-7.95°, 112.60°)."""
        for g in self.gedung_dict.values():
            self.assertTrue(math.isfinite(g.latitude))
            self.assertTrue(math.isfinite(g.longitude))
            self.assertTrue(-7.960 <= g.latitude <= -7.940, f"Latitude out of bounds: {g}")
            self.assertTrue(112.600 <= g.longitude <= 112.615, f"Longitude out of bounds: {g}")

    def test_gedung_oop_methods(self):
        """Menguji method OOP pada kelas Gedung (__repr__, __str__, __eq__, __hash__, __lt__)."""
        g1 = self.gedung_dict[1]
        g1_dup = Gedung(1, "Nama Lain", -7.947930, 112.606627)
        g2 = self.gedung_dict[2]

        self.assertEqual(g1, g1_dup)
        self.assertNotEqual(g1, g2)
        self.assertEqual(hash(g1), hash(g1_dup))
        self.assertTrue(g1 < g2)  # ID 1 < ID 2

        # Uji to_dict
        d = g1.to_dict()
        self.assertEqual(d["id"], 1)
        self.assertEqual(d["nama"], "Mabna Farobi")

    def test_haversine_distance_accuracy(self):
        """Menguji presisi fungsi Haversine terhadap jarak referensi bumi."""
        # Titik yang sama harus berjarak 0.0 meter
        self.assertEqual(hitung_haversine(-7.95, 112.60, -7.95, 112.60), 0.0)
        
        # Jarak Mabna Farobi (1) ke Kantin Al-Kautsar (4) ~ 104-105 meter
        g1 = self.gedung_dict[1]
        g4 = self.gedung_dict[4]
        d = g1.jarak_ke(g4)
        self.assertTrue(100.0 <= d <= 110.0, f"Jarak tidak wajar: {d}")

    # =========================================================================
    # 2. VALIDASI TOPOLOGI & KONEKTIVITAS JARINGAN JALAN KAMPUS
    # =========================================================================
    def test_graph_connectivity_bfs(self):
        """Memastikan seluruh 36 gedung terhubung dalam satu komponen utama (BFS)."""
        self.assertTrue(self.graph.is_connected(), "Graf kampus harus terhubung utuh!")
        comps = self.graph.get_connected_components()
        self.assertEqual(len(comps), 1)
        self.assertEqual(len(comps[0]), 36)

    def test_graph_symmetry_and_positive_weights(self):
        """Memastikan setiap ruas jalan bersifat dua arah (simetris) dengan bobot positif."""
        for u in self.gedung_dict.values():
            for v, w in self.graph.adj[u].items():
                self.assertIn(u, self.graph.adj[v], f"Sisi tidak simetris antara {u} dan {v}")
                w_rev = self.graph.adj[v][u]
                self.assertAlmostEqual(w, w_rev, places=4)
                self.assertTrue(w > 0.0, f"Bobot sisi harus positif: {w}")

    def test_total_network_statistics(self):
        """Memvalidasi metrik topologi jaringan default: 63 ruas jalan dan total panjang ~4.4 km."""
        summary = self.graph.summary()
        self.assertEqual(summary["total_gedung"], 36)
        self.assertEqual(summary["total_ruas_aktif"], 63)
        self.assertEqual(summary["total_ruas_ditutup"], 0)
        self.assertTrue(4000.0 <= summary["total_panjang_jalan_meter"] <= 5000.0)

    # =========================================================================
    # 3. PEMBUKTIAN ADMISSIBILITY & CONSISTENCY HEURISTIK HAVERSINE
    # =========================================================================
    def test_admissibility_on_all_edges(self):
        """
        Pembuktian Matematis & Empiris Admissibility:
        Untuk setiap sisi (u, v), bobot jalan pejalan kaki w(u, v) HARUS memenuhi:
        w(u, v) >= Haversine(u, v)
        """
        for u in self.gedung_dict.values():
            for v, w in self.graph.adj[u].items():
                d_hav = u.jarak_ke(v)
                self.assertTrue(
                    w >= (d_hav - 1e-9),
                    f"Pelanggaran Admissibility pada sisi ({u.nama} -> {v.nama}): w={w} < h={d_hav}"
                )

    # =========================================================================
    # 4. VERIFIKASI ALGORITMA PENCARIAN & KESESUAIAN BIAYA A* VS UCS
    # =========================================================================
    def test_start_equals_goal(self):
        """Kasus khusus simpul asal sama dengan simpul tujuan."""
        g1 = self.gedung_dict[1]
        res = astar_search(self.graph, g1, g1)
        self.assertTrue(res["success"])
        self.assertEqual(res["total_distance_meters"], 0.0)
        self.assertEqual(res["hop_count"], 0)
        self.assertEqual(res["nodes_expanded"], 0)
        self.assertEqual(res["nodes_popped"], 1)
        self.assertEqual(res["path"], [g1])

    def test_invalid_node_query(self):
        """Query dengan ID gedung fiktif wajib menghasilkan ValueError."""
        with self.assertRaises(ValueError):
            astar_search(self.graph, 999, 1)
        with self.assertRaises(ValueError):
            astar_search(self.graph, 1, 999)

    def test_three_representative_uas_scenarios(self):
        """Menguji 3 skenario navigasi nyata: jarak dekat, menengah, dan jauh lintas kampus."""
        # Skenario 1: Jarak Dekat (Mabna Farobi [1] -> Kantin Al-Kautsar [4])
        res1 = astar_search(self.graph, 1, 4)
        self.assertTrue(res1["success"])
        self.assertTrue(res1["total_distance_meters"] > 0)
        self.assertEqual(res1["path_ids"][0], 1)
        self.assertEqual(res1["path_ids"][-1], 4)

        # Skenario 2: Jarak Menengah (Pos Satpam Ma'had [10] -> Fak. Saintek [18])
        res2 = astar_search(self.graph, 10, 18)
        self.assertTrue(res2["success"])
        self.assertEqual(res2["path_ids"][0], 10)
        self.assertEqual(res2["path_ids"][-1], 18)

        # Skenario 3: Jarak Jauh Lintas Kampus (Mabna Farobi [1] -> Gedung SC [29])
        res3 = astar_search(self.graph, 1, 29)
        self.assertTrue(res3["success"])
        self.assertEqual(res3["path_ids"][0], 1)
        self.assertEqual(res3["path_ids"][-1], 29)
        # Verifikasi biaya A* identik dengan UCS pada Skenario 3
        res3_ucs = ucs_search(self.graph, 1, 29)
        self.assertAlmostEqual(res3["total_distance_meters"], res3_ucs["total_distance_meters"], places=2)

    def test_all_pairs_exhaustive_verification(self):
        """
        Uji Menyeluruh Seluruh 1.260 Pasangan Gedung (36 x 35):
        1. 0 Mismatch biaya antara A* dan UCS.
        2. A* tidak pernah mengekspansi lebih banyak simpul dibanding UCS.
        3. A* menghemat ekspansi simpul > 50%.
        """
        stats = verify_all_pairs(self.graph)
        self.assertEqual(stats["total_pairs"], 1260)
        self.assertEqual(stats["both_successful"], 1260)
        self.assertEqual(stats["cost_mismatches"], 0, "Biaya rute A* harus 100% identik dengan UCS!")
        self.assertEqual(stats["astar_more"], 0, "A* tidak boleh mengekspansi lebih banyak simpul dari UCS!")
        self.assertTrue(stats["reduction_pct"] > 50.0, f"Efisiensi A* harus > 50%, didapat {stats['reduction_pct']}%")

    def test_bfs_suboptimality_proof(self):
        """
        Pembuktian Teoretis & Empiris UAS:
        BFS terbukti menghasilkan jarak meter suboptimal pada sebagian pasangan
        karena BFS hanya meminimalkan jumlah langkah (hop count) tanpa orientasi bobot.
        """
        stats = verify_all_pairs(self.graph)
        self.assertTrue(
            stats["bfs_suboptimal_count"] > 0,
            "Harus terdapat pasangan di mana BFS menghasilkan rute meter yang tidak optimal!"
        )

    # =========================================================================
    # 5. SIMULASI RINTANGAN DINAMIS (DYNAMIC OBSTACLE & RE-ROUTING)
    # =========================================================================
    def test_dynamic_road_closure_and_rerouting(self):
        """
        Simulasi Penutupan Jalan Sementara:
        Tutup jalur utama antara Masjid Tarbiyah (13) dan Fak. Saintek (18).
        Pastikan A* secara dinamis menemukan rute memutar terbaik,
        dan ketika jalan dibuka kembali, rute kembali ke jalur utama.
        """
        g13 = self.gedung_dict[13]
        g18 = self.gedung_dict[18]

        # 1. Rute normal sebelum ditutup
        rute_awal = astar_search(self.graph, 13, 18)
        self.assertTrue(rute_awal["success"])
        self.assertEqual(rute_awal["path_ids"], [13, 18])
        biaya_awal = rute_awal["total_distance_meters"]

        # 2. Tutup ruas jalan 13 <-> 18
        tutup_sukses = self.graph.tutup_jalan(13, 18)
        self.assertTrue(tutup_sukses)
        self.assertNotIn((min(13, 18), max(13, 18)), self.graph.active_edges)

        # 3. Cari rute alternatif setelah penutupan jalan
        rute_memutar = astar_search(self.graph, 13, 18)
        self.assertTrue(rute_memutar["success"])
        self.assertNotEqual(rute_memutar["path_ids"], [13, 18])
        # Rute alternatif harus memutar sehingga jaraknya lebih panjang
        self.assertTrue(rute_memutar["total_distance_meters"] > biaya_awal)

        # 4. Buka kembali jalan
        buka_sukses = self.graph.buka_jalan(13, 18)
        self.assertTrue(buka_sukses)
        self.assertIn((min(13, 18), max(13, 18)), self.graph.active_edges)

        # 5. Rute kembali optimal ke jalur langsung
        rute_pulih = astar_search(self.graph, 13, 18)
        self.assertEqual(rute_pulih["path_ids"], [13, 18])
        self.assertAlmostEqual(rute_pulih["total_distance_meters"], biaya_awal, places=2)

    # =========================================================================
    # 6. PENGUJIAN REGRESI CACAT ALGORITMA & EDGE CASES (FLAW ANALYSIS)
    # =========================================================================
    def test_boolean_coordinates_rejected(self):
        """Mencegah kerentanan injeksi boolean pada koordinat Gedung."""
        with self.assertRaises(TypeError):
            Gedung(99, "Gedung Uji", True, 112.60)
        with self.assertRaises(TypeError):
            Gedung(99, "Gedung Uji", -7.95, False)

    def test_get_gedung_exact_match_priority(self):
        """Memastikan pencarian exact match diprioritaskan sebelum substring match."""
        # Uji exact match
        g_exact = self.graph.get_gedung("Gedung Rektorat")
        self.assertIsNotNone(g_exact)
        self.assertEqual(g_exact.id, 20)

        # Uji pencarian substring
        g_sub = self.graph.get_gedung("Rektorat")
        self.assertIsNotNone(g_sub)
        self.assertEqual(g_sub.id, 20)

    def test_closed_road_error_cases(self):
        """Menguji penanganan penutupan/pembukaan jalan yang tidak valid."""
        # Menutup jalan yang tidak ada
        self.assertFalse(self.graph.tutup_jalan(1, 29))
        
        # Membuka jalan yang memang aktif (tidak dalam daftar closed)
        self.assertFalse(self.graph.buka_jalan(1, 2))

        # Query penutupan dengan ID tidak valid
        with self.assertRaises(ValueError):
            self.graph.tutup_jalan(999, 1)

        # Membuka jalan yang tidak pernah ditutup dan tidak ada di graf (mencegah penambahan sisi liar)
        self.assertFalse(self.graph.buka_jalan(1, 36))
        self.assertNotIn((1, 36), self.graph.active_edges)

    def test_gedung_self_distance_strictly_zero(self):
        """Memastikan jarak Haversine suatu gedung ke dirinya sendiri bernilai tepat 0.0."""
        for g in self.gedung_dict.values():
            self.assertEqual(g.jarak_ke(g), 0.0)

    def test_gedung_whitespace_normalization(self):
        """Memastikan nama dan kategori dibersihkan dari spasi ganda."""
        g = Gedung(99, "  Gedung    Uji   Spasi   Ganda ", -7.950, 112.605, "  Kategori   Uji  ")
        self.assertEqual(g.nama, "Gedung Uji Spasi Ganda")
        self.assertEqual(g.kategori, "Kategori Uji")

    def test_compare_algorithms_unreachable(self):
        """Memastikan compare_algorithms menangani kondisi graf terputus tanpa galat."""
        self.graph.tutup_jalan(1, 2)
        self.graph.tutup_jalan(1, 3)
        try:
            comp = compare_algorithms(self.graph, 1, 4)
            self.assertFalse(comp["astar"]["success"])
            self.assertFalse(comp["ucs"]["success"])
            self.assertTrue(comp["cost_match_astar_ucs"])  # Keduanya sepakat rute tak terjangkau
        finally:
            self.graph.buka_jalan(1, 2)
            self.graph.buka_jalan(1, 3)

    def test_total_cost_key_present_in_all_algorithms(self):
        """Memastikan kunci 'total_cost' hadir dan konsisten pada A*, UCS, dan BFS."""
        res_a = astar_search(self.graph, 1, 4)
        res_u = ucs_search(self.graph, 1, 4)
        res_b = bfs_search(self.graph, 1, 4)

        for res in [res_a, res_u, res_b]:
            self.assertIn("total_cost", res)
            self.assertIn("total_distance_meters", res)
            self.assertEqual(res["total_cost"], res["total_distance_meters"])

    def test_path_integrity_and_weight_consistency(self):
        """
        Memverifikasi integritas rute:
        Setiap pasangan simpul berurutan pada path harus bertetangga di graf,
        dan akumulasi bobot ruas harus tepat sama dengan total_cost.
        """
        res = astar_search(self.graph, 1, 29)
        path = res["path"]
        self.assertTrue(len(path) >= 2)

        accumulated_dist = 0.0
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]
            self.assertIn(v, self.graph.adj[u], f"Ruas ({u.nama} -> {v.nama}) tidak ada di graf!")
            accumulated_dist += self.graph.adj[u][v]

        self.assertAlmostEqual(res["total_cost"], accumulated_dist, places=2)

    def test_disconnected_graph_handling(self):
        """
        Menguji ketahanan algoritma ketika simpul terisolasi (graf terputus):
        A* dan UCS harus menghasilkan success=False, path=[], total_cost=None tanpa crash.
        """
        # Isolasi Mabna Farobi (1) dengan menutup sisi ke (2) dan (3)
        self.graph.tutup_jalan(1, 2)
        self.graph.tutup_jalan(1, 3)

        try:
            res_a = astar_search(self.graph, 1, 4)
            self.assertFalse(res_a["success"])
            self.assertEqual(res_a["path"], [])
            self.assertIsNone(res_a["total_cost"])
            self.assertIsNone(res_a["total_distance_meters"])

            res_u = ucs_search(self.graph, 1, 4)
            self.assertFalse(res_u["success"])
            self.assertEqual(res_u["path"], [])
            self.assertIsNone(res_u["total_cost"])

            res_b = bfs_search(self.graph, 1, 4)
            self.assertFalse(res_b["success"])
            self.assertEqual(res_b["path"], [])
            self.assertIsNone(res_b["total_cost"])
        finally:
            # Pulihkan kembali jalan yang ditutup agar setUpClass tidak terpengaruh
            self.graph.buka_jalan(1, 2)
            self.graph.buka_jalan(1, 3)


if __name__ == "__main__":
    unittest.main()
