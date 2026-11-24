"""
=============================================================================
VISUALISASI GRAF SPASIAL KAMPUS & RUTE A* (TAHAP UAS)
Mata Kuliah : Artificial Intelligence (Semester 5 OBE)
Institusi   : Teknik Informatika, UIN Maulana Malik Ibrahim Malang
Deskripsi   : Modul visualisasi graf 2D spasial berbasis koordinat GPS nyata
              (Latitude vs Longitude) menggunakan Matplotlib. Menampilkan 36 gedung
              berwarna per kategori, 63 ruas jalan, dan rute navigasi A* optimal.
=============================================================================
"""

import os
import sys
import tempfile
# Arahkan cache directory matplotlib ke folder temporary sistem
os.environ.setdefault('MPLCONFIGDIR', tempfile.gettempdir())

# Tambahkan direktori modul ke sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

import argparse
from typing import Optional, List, Dict, Union, Any

# Gunakan backend non-interaktif 'Agg' agar rendering ke PNG berjalan mulus di terminal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from gedung import Gedung
from campus_network import CampusGraph, create_default_campus_graph
from search_engine import astar_search

# Palet warna kategori akademik profesional
COLOR_PALETTE: Dict[str, str] = {
    "Fakultas": "#1D4ED8",           # Blue
    "Ma'had Putra": "#15803D",       # Green
    "Ma'had Putri": "#9333EA",       # Purple
    "Masjid Kampus": "#0D9488",      # Teal
    "Rektorat & Biro": "#B91C1C",    # Crimson Red
    "Perpustakaan": "#D97706",       # Amber
    "Gedung Kuliah": "#4F46E5",      # Indigo
    "Sarana Olahraga": "#EA580C",    # Orange
    "Layanan Kampus": "#475569",     # Slate
    "Layanan Kesehatan": "#E11D48",  # Rose
    "Layanan Umum": "#64748B",       # Muted Slate
    "Administrasi Ma'had": "#047857",# Dark Emerald
    "Keamanan Ma'had": "#334155",    # Dark Slate
    "Ibadah & Majelis": "#059669",   # Emerald
    "Kantin & Logistik": "#CA8A04",  # Yellow-Brown
    "Asrama Takmir": "#166534",      # Dark Green
    "Media & Informasi": "#2563EB",  # Royal Blue
    "Landmark Kampus": "#7C3AED",    # Violet
    "Akademik": "#3B82F6",           # Sky Blue
}


def plot_campus_network(
    graph: CampusGraph,
    path_gedung: Optional[List[Gedung]] = None,
    output_path: str = "peta_kampus_rute.png",
    title: Optional[str] = None
) -> str:
    """
    Menggambar peta spasial 2D jaringan jalan Kampus 1 UIN Maulana Malik Ibrahim Malang.
    
    Fitur:
    - Sumbu X = Bujur Timur (Longitude), Sumbu Y = Lintang Selatan (Latitude).
    - Seluruh ruas jalan digambar sebagai garis koneksi abu-abu.
    - Sisi jalan yang ditutup sementara digambar dengan garis putus-putus merah.
    - 36 simpul gedung digambar dengan warna berbeda sesuai kategori fasilitas.
    - Rute A* disorot tebal dengan warna merah menyala (#DC2626) dan penanda simpul rute.
    - Simpul awal ditandai hijau (#16A34A), simpul tujuan ditandai emas (#F59E0B).
    
    Parameter:
        graph: Objek CampusGraph aktif
        path_gedung: Daftar objek Gedung rute solusi A* (opsional)
        output_path: Jalur penyimpanan berkas gambar PNG
        title: Judul plot (opsional)
        
    Kembalian:
        Jalur absolut berkas gambar yang dihasilkan.
    """
    fig, ax = plt.subplots(figsize=(15, 12), dpi=250)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#FFFFFF')

    # 1. Gambar seluruh ruas jalan aktif
    for (u_id, v_id) in graph.active_edges:
        g_u = graph.gedung_dict[u_id]
        g_v = graph.gedung_dict[v_id]
        ax.plot(
            [g_u.longitude, g_v.longitude],
            [g_u.latitude, g_v.latitude],
            color='#CBD5E1',
            linewidth=1.4,
            linestyle='-',
            zorder=1
        )

    # 2. Gambar ruas jalan yang ditutup (jika ada)
    for (u_id, v_id) in graph.closed_edges:
        g_u = graph.gedung_dict[u_id]
        g_v = graph.gedung_dict[v_id]
        ax.plot(
            [g_u.longitude, g_v.longitude],
            [g_u.latitude, g_v.latitude],
            color='#EF4444',
            linewidth=2.0,
            linestyle='--',
            alpha=0.8,
            zorder=2,
            label="Jalan Ditutup" if u_id == list(graph.closed_edges.keys())[0][0] else ""
        )

    # 3. Gambar sorotan rute solusi A* (jika ada)
    path_edges_set = set()
    if path_gedung and len(path_gedung) > 1:
        path_lons = [g.longitude for g in path_gedung]
        path_lats = [g.latitude for g in path_gedung]

        # Garis lintasan tebal
        ax.plot(
            path_lons,
            path_lats,
            color='#DC2626',
            linewidth=4.0,
            linestyle='-',
            solid_capstyle='round',
            alpha=0.95,
            zorder=5,
            label="Rute Solusi A* Search"
        )

        for i in range(len(path_gedung) - 1):
            path_edges_set.add((min(path_gedung[i].id, path_gedung[i+1].id), max(path_gedung[i].id, path_gedung[i+1].id)))

    # 4. Gambar simpul 36 gedung
    categories_present = set()
    for g in graph.gedung_dict.values():
        color = COLOR_PALETTE.get(g.kategori, "#64748B")
        categories_present.add((g.kategori, color))

        # Ukuran simpul (lebih besar jika bagian dari rute solusi)
        is_in_path = path_gedung and (g in path_gedung)
        node_size = 110 if is_in_path else 65
        edge_color = '#DC2626' if is_in_path else '#334155'
        edge_width = 2.0 if is_in_path else 1.0

        ax.scatter(
            g.longitude,
            g.latitude,
            s=node_size,
            color=color,
            edgecolors=edge_color,
            linewidths=edge_width,
            zorder=6
        )

        # Label nomor ID dan Nama Gedung
        short_name = g.nama
        if len(short_name) > 18:
            short_name = short_name[:16] + ".."
            
        label_text = f"[{g.id}] {short_name}"
        
        # Penyesuaian posisi teks agar tidak saling tumpang tindih
        dx = 0.00004
        dy = 0.00003 if g.id % 2 == 0 else -0.00004
        
        ax.text(
            g.longitude + dx,
            g.latitude + dy,
            label_text,
            fontsize=7.2,
            fontweight='bold' if is_in_path else 'normal',
            color='#0F172A' if is_in_path else '#475569',
            bbox=dict(
                boxstyle="round,pad=0.18",
                facecolor="#FEF2F2" if is_in_path else "#F8FAFC",
                edgecolor="#EF4444" if is_in_path else "#E2E8F0",
                alpha=0.88,
                linewidth=0.8
            ),
            zorder=7
        )

    # 5. Sorot simpul start dan goal secara khusus
    if path_gedung and len(path_gedung) >= 1:
        start_g = path_gedung[0]
        goal_g = path_gedung[-1]

        # Start Marker (Hijau)
        ax.scatter(
            start_g.longitude,
            start_g.latitude,
            s=220,
            color='#16A34A',
            edgecolors='#FFFFFF',
            linewidths=2.5,
            marker='o',
            zorder=8,
            label=f"Start: [{start_g.id}] {start_g.nama}"
        )

        # Goal Marker (Bintang Emas)
        ax.scatter(
            goal_g.longitude,
            goal_g.latitude,
            s=260,
            color='#F59E0B',
            edgecolors='#78350F',
            linewidths=1.8,
            marker='*',
            zorder=8,
            label=f"Goal: [{goal_g.id}] {goal_g.nama}"
        )

    # 6. Format Sumbu Koordinat Geospasial
    ax.set_xlabel("Bujur Timur (Longitude °E)", fontsize=10, fontweight='bold', color='#1E293B', labelpad=8)
    ax.set_ylabel("Lintang Selatan (Latitude °S)", fontsize=10, fontweight='bold', color='#1E293B', labelpad=8)
    ax.tick_params(colors='#475569', labelsize=8.5)
    ax.grid(True, linestyle=':', alpha=0.5, color='#94A3B8')

    # Format angka desimal pada tick
    ax.xaxis.set_major_formatter(plt.FormatStrFormatter('%.4f'))
    ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.4f'))

    # 7. Judul dan Keterangan
    if title is None:
        if path_gedung:
            title = f"Peta Geospasial Kampus 1 UIN Malang — Navigasi A* Search [{path_gedung[0].nama} -> {path_gedung[-1].nama}]"
        else:
            title = "Peta Geospasial Topologi Jaringan Jalan Kampus 1 UIN Maulana Malik Ibrahim Malang"

    ax.set_title(title, fontsize=12.5, fontweight='bold', color='#0F172A', pad=14)

    # 8. Legend / Legenda
    legend_elements = []
    
    # Elemen rute & penanda
    if path_gedung and len(path_gedung) > 1:
        legend_elements.append(
            mpatches.Patch(color='#DC2626', label=f"Rute A* ({len(path_gedung)-1} ruas)")
        )
    legend_elements.append(
        mpatches.Patch(color='#CBD5E1', label=f"Ruas Jalan ({len(graph.active_edges)} jalur aktif)")
    )
    if graph.closed_edges:
        legend_elements.append(
            mpatches.Patch(color='#EF4444', label=f"Jalan Ditutup ({len(graph.closed_edges)} rintangan)")
        )

    # Elemen kategori gedung
    category_patches = [
        mpatches.Patch(color=c, label=kat)
        for kat, c in sorted(categories_present)
    ]

    # Buat dua legenda terpisah atau gabungkan
    all_legends = legend_elements + category_patches
    ax.legend(
        handles=all_legends,
        loc='upper left',
        bbox_to_anchor=(1.01, 1.0),
        fontsize=8.0,
        frameon=True,
        facecolor='#FFFFFF',
        edgecolor='#CBD5E1',
        title="Legenda Fasilitas & Jalur",
        title_fontsize=9.0
    )

    plt.tight_layout()

    # Simpan ke file gambar (pastikan jalur relatif disimpan di direktori modul project)
    if not os.path.isabs(output_path):
        abs_output = os.path.join(_current_dir, output_path)
    else:
        abs_output = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(abs_output), exist_ok=True)
    plt.savefig(abs_output, bbox_inches='tight', dpi=250)
    plt.close(fig)

    return abs_output


def main():
    parser = argparse.ArgumentParser(
        description="Visualisasi Spasial Graf Kampus 1 UIN Malang & Rute A* Search (Tahap UAS)."
    )
    parser.add_argument(
        "--start",
        type=str,
        default="1",
        help="ID atau Nama Gedung Asal (default: 1 - Mabna Farobi)"
    )
    parser.add_argument(
        "--goal",
        type=str,
        default="29",
        help="ID atau Nama Gedung Tujuan (default: 29 - Gedung SC)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="peta_kampus_rute.png",
        help="Nama berkas luaran gambar PNG (default: peta_kampus_rute.png)"
    )
    parser.add_argument(
        "--no-route",
        action="store_true",
        help="Hanya menggambar jaringan jalan tanpa menghitung rute A*"
    )

    args = parser.parse_args()

    graph = create_default_campus_graph()
    
    if args.no_route:
        out_file = plot_campus_network(graph, path_gedung=None, output_path=args.output)
        print(f"Peta jaringan kampus berhasil disimpan ke: {out_file}")
    else:
        res = astar_search(graph, args.start, args.goal)
        if res["success"]:
            print(f"Rute A* ditemukan: {' -> '.join(res['path_names'])}")
            print(f"Total Jarak Riil : {res['total_distance_meters']:.1f} meter")
            print(f"Jumlah Ruas     : {res['hop_count']} langkah")
            out_file = plot_campus_network(
                graph,
                path_gedung=res["path"],
                output_path=args.output,
                title=f"Rute Navigasi A* Kampus 1 UIN Malang: [{res['start'].nama}] -> [{res['goal'].nama}] ({res['total_distance_meters']:.1f} m)"
            )
            print(f"Gambar visualisasi rute berhasil disimpan ke: {out_file}")
        else:
            print(f"Pencarian rute gagal: {res['message']}")
            out_file = plot_campus_network(graph, path_gedung=None, output_path=args.output)
            print(f"Peta dasar disimpan ke: {out_file}")


if __name__ == "__main__":
    main()
