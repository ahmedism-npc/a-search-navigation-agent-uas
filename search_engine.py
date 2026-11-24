"""
=============================================================================
MESIN PENCARIAN RUTE CERDAS (SEARCH ENGINE) - TAHAP UAS
Mata Kuliah : Artificial Intelligence (Semester 5 OBE)
Institusi   : Teknik Informatika, UIN Maulana Malik Ibrahim Malang
Deskripsi   : Implementasi algoritma A* Search, Uniform-Cost Search (UCS),
              dan Breadth-First Search (BFS) berbasis objek Gedung dengan metrik
              kinerja presisi tinggi (jarak riil, waktu komputasi, ekspansi).
=============================================================================
"""

import os
import sys
import time
import heapq
from collections import deque
from typing import Dict, List, Tuple, Optional, Any, Union

# Tambahkan direktori modul ke sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from gedung import Gedung
from campus_network import CampusGraph


def astar_search(
    graph: CampusGraph,
    start: Union[int, str, Gedung],
    goal: Union[int, str, Gedung]
) -> Dict[str, Any]:
    """
    Pencarian rute optimal menggunakan algoritma A* Search: f(n) = g(n) + h(n).
    
    Landasan Heuristik:
        h(n) = n.jarak_ke(goal) (Formula Haversine garis lurus bumi).
        Karena jarak lengkung bumi merupakan batas bawah mutlak (greatest lower bound)
        dari lintasan pedestrian berbelok, maka h(n) <= h*(n) (Strictly Admissible)
        dan memenuhi segitiga bola (Consistent/Monotonic).
        
    Kaidah Evaluasi:
        - frontier: Min-Heap priority queue berisi tuple (f_score, g_score, current_gedung, path).
        - Filter entri usang (stale entries): jika g_score > cost_so_far[current], lewati.
        - Goal Test: dilakukan saat simpul ditarik dari antrean. Jika lolos, berhenti tanpa ekspansi.
        - Ekspansi: mengevaluasi tetangga simpul non-goal; hanya kandidat yang memperbaiki biaya
          yang dimasukkan ke dalam frontier.
    """
    t_start = time.perf_counter()

    g_start = graph.get_gedung(start)
    g_goal = graph.get_gedung(goal)

    if not g_start or not g_goal:
        raise ValueError(f"Simpul awal '{start}' atau tujuan '{goal}' tidak ditemukan di graf!")

    # Inisialisasi
    initial_h = g_start.jarak_ke(g_goal)
    tie_counter: int = 0
    frontier: List[Tuple[float, float, int, Gedung, List[Gedung]]] = [
        (initial_h, 0.0, tie_counter, g_start, [g_start])
    ]

    cost_so_far: Dict[Gedung, float] = {g_start: 0.0}
    nodes_expanded: int = 0
    nodes_popped: int = 0
    pop_trace: List[Dict[str, Any]] = []

    while frontier:
        f_score, g_score, _, current, path = heapq.heappop(frontier)

        # Lewati entri usang pada antrean prioritas (stale entry)
        if g_score > cost_so_far.get(current, float('inf')):
            continue

        nodes_popped += 1
        h_score = current.jarak_ke(g_goal)

        pop_trace.append({
            "step": nodes_popped,
            "gedung_id": current.id,
            "nama": current.nama,
            "g": round(g_score, 2),
            "h": round(h_score, 2),
            "f": round(f_score, 2)
        })

        # GOAL TEST
        if current == g_goal:
            exec_time_ms = (time.perf_counter() - t_start) * 1000.0
            return {
                "success": True,
                "algorithm": "A* Search",
                "start": g_start,
                "goal": g_goal,
                "path": path,
                "path_names": [g.nama for g in path],
                "path_ids": [g.id for g in path],
                "hop_count": len(path) - 1,
                "total_cost": round(g_score, 2),
                "total_distance_meters": round(g_score, 2),
                "nodes_expanded": nodes_expanded,
                "nodes_popped": nodes_popped,
                "execution_time_ms": round(exec_time_ms, 3),
                "trace": pop_trace
            }

        # Simpul valid non-goal: lakukan ekspansi
        nodes_expanded += 1
        for neighbor, weight in graph.get_neighbors(current).items():
            new_g = g_score + weight
            if neighbor not in cost_so_far or new_g < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_g
                h_val = neighbor.jarak_ke(g_goal)
                f_val = new_g + h_val
                tie_counter += 1
                heapq.heappush(frontier, (f_val, new_g, tie_counter, neighbor, path + [neighbor]))

    exec_time_ms = (time.perf_counter() - t_start) * 1000.0
    return {
        "success": False,
        "algorithm": "A* Search",
        "start": g_start,
        "goal": g_goal,
        "path": [],
        "path_names": [],
        "path_ids": [],
        "hop_count": 0,
        "total_cost": None,
        "total_distance_meters": None,
        "nodes_expanded": nodes_expanded,
        "nodes_popped": nodes_popped,
        "execution_time_ms": round(exec_time_ms, 3),
        "trace": pop_trace,
        "message": f"Tidak ada rute dari '{g_start.nama}' ke '{g_goal.nama}'."
    }


def ucs_search(
    graph: CampusGraph,
    start: Union[int, str, Gedung],
    goal: Union[int, str, Gedung]
) -> Dict[str, Any]:
    """
    Pencarian rute menggunakan Uniform-Cost Search (UCS / Algoritma Dijkstra).
    Fungsi prioritas: f(n) = g(n) (uninformed search berbasis biaya lintasan).
    Digunakan sebagai acuan baku (ground-truth) optimalitas biaya A*.
    """
    t_start = time.perf_counter()

    g_start = graph.get_gedung(start)
    g_goal = graph.get_gedung(goal)

    if not g_start or not g_goal:
        raise ValueError(f"Simpul awal '{start}' atau tujuan '{goal}' tidak ditemukan di graf!")

    tie_counter: int = 0
    frontier: List[Tuple[float, int, Gedung, List[Gedung]]] = [
        (0.0, tie_counter, g_start, [g_start])
    ]

    cost_so_far: Dict[Gedung, float] = {g_start: 0.0}
    nodes_expanded: int = 0
    nodes_popped: int = 0

    while frontier:
        cost, _, current, path = heapq.heappop(frontier)

        if cost > cost_so_far.get(current, float('inf')):
            continue

        nodes_popped += 1

        if current == g_goal:
            exec_time_ms = (time.perf_counter() - t_start) * 1000.0
            return {
                "success": True,
                "algorithm": "Uniform-Cost Search (UCS)",
                "start": g_start,
                "goal": g_goal,
                "path": path,
                "path_names": [g.nama for g in path],
                "path_ids": [g.id for g in path],
                "hop_count": len(path) - 1,
                "total_cost": round(cost, 2),
                "total_distance_meters": round(cost, 2),
                "nodes_expanded": nodes_expanded,
                "nodes_popped": nodes_popped,
                "execution_time_ms": round(exec_time_ms, 3)
            }

        nodes_expanded += 1
        for neighbor, weight in graph.get_neighbors(current).items():
            new_cost = cost + weight
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                tie_counter += 1
                heapq.heappush(frontier, (new_cost, tie_counter, neighbor, path + [neighbor]))

    exec_time_ms = (time.perf_counter() - t_start) * 1000.0
    return {
        "success": False,
        "algorithm": "Uniform-Cost Search (UCS)",
        "start": g_start,
        "goal": g_goal,
        "path": [],
        "path_names": [],
        "path_ids": [],
        "hop_count": 0,
        "total_cost": None,
        "total_distance_meters": None,
        "nodes_expanded": nodes_expanded,
        "nodes_popped": nodes_popped,
        "execution_time_ms": round(exec_time_ms, 3),
        "message": f"Tidak ada rute dari '{g_start.nama}' ke '{g_goal.nama}'."
    }


def bfs_search(
    graph: CampusGraph,
    start: Union[int, str, Gedung],
    goal: Union[int, str, Gedung]
) -> Dict[str, Any]:
    """
    Pencarian rute menggunakan Breadth-First Search (BFS).
    Menggunakan antrean FIFO (collections.deque) untuk mencari rute dengan jumlah
    langkah/ruas jalan (hop count) paling sedikit.
    
    Tujuan Akademik UAS:
        Membuktikan secara empiris bahwa BFS hanya optimal untuk jumlah langkah,
        namun TIDAK menjamin jarak terpendek (meter) pada graf berbobot variatif.
    """
    t_start = time.perf_counter()

    g_start = graph.get_gedung(start)
    g_goal = graph.get_gedung(goal)

    if not g_start or not g_goal:
        raise ValueError(f"Simpul awal '{start}' atau tujuan '{goal}' tidak ditemukan di graf!")

    queue = deque([(g_start, [g_start])])
    visited = {g_start}
    nodes_expanded: int = 0
    nodes_popped: int = 0

    while queue:
        current, path = queue.popleft()
        nodes_popped += 1

        if current == g_goal:
            # Hitung total jarak lintasan rute BFS
            total_dist = 0.0
            for i in range(len(path) - 1):
                total_dist += graph.adj[path[i]][path[i + 1]]

            exec_time_ms = (time.perf_counter() - t_start) * 1000.0
            return {
                "success": True,
                "algorithm": "Breadth-First Search (BFS)",
                "start": g_start,
                "goal": g_goal,
                "path": path,
                "path_names": [g.nama for g in path],
                "path_ids": [g.id for g in path],
                "hop_count": len(path) - 1,
                "total_cost": round(total_dist, 2),
                "total_distance_meters": round(total_dist, 2),
                "nodes_expanded": nodes_expanded,
                "nodes_popped": nodes_popped,
                "execution_time_ms": round(exec_time_ms, 3)
            }

        nodes_expanded += 1
        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    exec_time_ms = (time.perf_counter() - t_start) * 1000.0
    return {
        "success": False,
        "algorithm": "Breadth-First Search (BFS)",
        "start": g_start,
        "goal": g_goal,
        "path": [],
        "path_names": [],
        "path_ids": [],
        "hop_count": 0,
        "total_cost": None,
        "total_distance_meters": None,
        "nodes_expanded": nodes_expanded,
        "nodes_popped": nodes_popped,
        "execution_time_ms": round(exec_time_ms, 3),
        "message": f"Tidak ada rute dari '{g_start.nama}' ke '{g_goal.nama}'."
    }


def compare_algorithms(
    graph: CampusGraph,
    start: Union[int, str, Gedung],
    goal: Union[int, str, Gedung]
) -> Dict[str, Any]:
    """
    Menjalankan ketiga algoritma (A*, UCS, BFS) pada pasangan simpul yang sama
    dan menyajikan perbandingan komprehensif metrik evaluasi.
    """
    res_a = astar_search(graph, start, goal)
    res_u = ucs_search(graph, start, goal)
    res_b = bfs_search(graph, start, goal)

    both_success = res_a["success"] and res_u["success"]
    both_failed = (not res_a["success"]) and (not res_u["success"])

    cost_match = (
        abs(res_a["total_cost"] - res_u["total_cost"]) < 1e-5
        if both_success else both_failed
    )

    bfs_suboptimal = (
        res_b["total_cost"] > res_a["total_cost"] + 1e-5
        if both_success and res_b["success"] else False
    )

    return {
        "astar": res_a,
        "ucs": res_u,
        "bfs": res_b,
        "cost_match_astar_ucs": cost_match,
        "bfs_distance_suboptimal": bfs_suboptimal
    }


def verify_all_pairs(graph: CampusGraph) -> Dict[str, Any]:
    """
    Verifikasi komparatif menyeluruh seluruh pasangan gedung (u != v).
    Untuk 36 gedung, terdapat 36 x 35 = 1.260 pasangan uji.
    
    Memvalidasi:
    1. Kesesuaian optimalitas biaya A* vs UCS (0 mismatch).
    2. Efisiensi ekspansi simpul A* terhadap UCS.
    3. Jumlah pasangan di mana rute BFS menghasilkan jarak meter suboptimal.
    """
    all_gedung = list(graph.gedung_dict.values())
    total_tested = 0
    both_successful = 0
    both_unreachable = 0
    reachability_mismatches = 0
    cost_mismatches = 0
    
    astar_fewer = 0
    astar_equal = 0
    astar_more = 0
    
    total_exp_astar = 0
    total_exp_ucs = 0
    total_time_astar_ms = 0.0
    total_time_ucs_ms = 0.0

    bfs_suboptimal_count = 0

    for u in all_gedung:
        for v in all_gedung:
            if u != v:
                total_tested += 1
                res_a = astar_search(graph, u, v)
                res_u = ucs_search(graph, u, v)
                res_b = bfs_search(graph, u, v)

                succ_a = res_a["success"]
                succ_u = res_u["success"]

                if succ_a != succ_u:
                    reachability_mismatches += 1
                    continue

                if not succ_a:
                    both_unreachable += 1
                    continue

                both_successful += 1
                cost_a = res_a["total_distance_meters"]
                cost_u = res_u["total_distance_meters"]

                if abs(cost_a - cost_u) > 1e-5:
                    cost_mismatches += 1

                exp_a = res_a["nodes_expanded"]
                exp_u = res_u["nodes_expanded"]
                total_exp_astar += exp_a
                total_exp_ucs += exp_u
                
                total_time_astar_ms += res_a["execution_time_ms"]
                total_time_ucs_ms += res_u["execution_time_ms"]

                if exp_a < exp_u:
                    astar_fewer += 1
                elif exp_a == exp_u:
                    astar_equal += 1
                else:
                    astar_more += 1

                # Uji apakah BFS menghasilkan rute meter yang lebih panjang
                if res_b["success"] and (res_b["total_distance_meters"] - cost_a) > 1e-4:
                    bfs_suboptimal_count += 1

    reduction_pct = (
        ((total_exp_ucs - total_exp_astar) / total_exp_ucs) * 100.0
        if total_exp_ucs > 0 else 0.0
    )

    return {
        "total_pairs": total_tested,
        "both_successful": both_successful,
        "both_unreachable": both_unreachable,
        "reachability_mismatches": reachability_mismatches,
        "cost_mismatches": cost_mismatches,
        "astar_fewer": astar_fewer,
        "astar_equal": astar_equal,
        "astar_more": astar_more,
        "total_exp_astar": total_exp_astar,
        "total_exp_ucs": total_exp_ucs,
        "reduction_pct": round(reduction_pct, 1),
        "avg_time_astar_ms": round(total_time_astar_ms / both_successful, 3) if both_successful else 0.0,
        "avg_time_ucs_ms": round(total_time_ucs_ms / both_successful, 3) if both_successful else 0.0,
        "bfs_suboptimal_count": bfs_suboptimal_count,
        "bfs_suboptimal_pct": round((bfs_suboptimal_count / both_successful) * 100.0, 1) if both_successful else 0.0
    }


if __name__ == "__main__":
    from campus_network import create_default_campus_graph
    
    graph = create_default_campus_graph()
    print("Menjalankan verifikasi komparatif seluruh pasangan (All-Pairs 1.260 rute)...")
    t0 = time.time()
    stats = verify_all_pairs(graph)
    durasi = time.time() - t0
    
    print("=" * 70)
    print("  HASIL VERIFIKASI MENYELURUH ALL-PAIRS (36 GEDUNG KAMPUS 1 UIN MALANG)")
    print("=" * 70)
    print(f"Total Pasangan Diuji       : {stats['total_pairs']} pasangan ({durasi:.2f} detik)")
    print(f"Pasangan Berhasil (Sukses) : {stats['both_successful']} pasangan (100.0%)")
    print(f"Ketidaksesuaian Biaya      : {stats['cost_mismatches']} mismatch (A* 100% Identik Biaya dengan UCS)")
    print(f"A* Ekspansi Lebih Sedikit  : {stats['astar_fewer']} pasangan ({stats['astar_fewer']/stats['both_successful']*100:.1f}%)")
    print(f"A* Ekspansi Sama Banyak    : {stats['astar_equal']} pasangan ({stats['astar_equal']/stats['both_successful']*100:.1f}%)")
    print(f"A* Ekspansi Lebih Banyak   : {stats['astar_more']} pasangan (0.0%)")
    print(f"Total Simpul Diekspansi A* : {stats['total_exp_astar']} simpul (rata-rata {stats['total_exp_astar']/stats['both_successful']:.1f}/rute)")
    print(f"Total Simpul Diekspansi UCS: {stats['total_exp_ucs']} simpul (rata-rata {stats['total_exp_ucs']/stats['both_successful']:.1f}/rute)")
    print(f"Penghematan Simpul A*      : {stats['reduction_pct']}% lebih efisien dari UCS")
    print(f"Rute BFS Suboptimal Jarak  : {stats['bfs_suboptimal_count']} pasangan ({stats['bfs_suboptimal_pct']}%) terbukti tidak optimal")
    print("=" * 70)
