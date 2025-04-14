# Heuristic Search GUI with Tkinter

Program ini adalah aplikasi Python dengan antarmuka grafis (GUI) yang mendemonstrasikan dua algoritma pencarian berbasis heuristik, yaitu:

- **Greedy Best First Search**
- **A* Search**

Aplikasi ini menggunakan `Tkinter` untuk GUI, `NetworkX` untuk struktur graf, dan `Matplotlib` untuk visualisasi graf.

## Fitur

- Visualisasi graf interaktif lengkap dengan bobot dan nilai heuristik tiap node.
- Penghitungan nilai heuristik otomatis menggunakan algoritma Dijkstra.
- Perbandingan hasil pencarian antara algoritma Greedy dan A*.
- Tampilan rute pencarian langsung di graf.

## Struktur Graf

Graf yang digunakan bersifat statis dan didefinisikan dalam bentuk dictionary Python seperti ini:

```python
graph = {
    "A": {"B": 2, "C": 3},
    "B": {"A": 2, "D": 4, "E": 5},
    ...
}
```

Posisi node untuk visualisasi ditentukan manual menggunakan koordinat:

```python
node_positions = {
    "A": (0, 2),
    "B": (1, 3),
    ...
}
```

## Cara Menjalankan

1. Pastikan Python sudah terinstal (direkomendasikan Python 3.8+).
2. Instal dependensi yang dibutuhkan:

```bash
pip install matplotlib networkx
```

3. Jalankan program:

```bash
python nama_file.py
```

## Algoritma yang Digunakan

### Greedy Best First Search
- Memilih node dengan nilai heuristik terendah.
- Tidak memperhatikan total cost (biaya perjalanan sejauh ini).

### A* Search
- Menggunakan formula: `f(n) = g(n) + h(n)`
    - `g(n)` = total cost sejauh ini
    - `h(n)` = heuristik ke tujuan
- Menggabungkan strategi eksplorasi dan eksploitatif.

## Tampilan

![demo](/assets/demo.png)

Antarmuka program menampilkan:
- Dropdown untuk memilih node awal dan tujuan
- Tombol "Cari Rute" untuk menjalankan algoritma
- Visualisasi graf dengan warna:
    - 🔴 A* Path
    - 🟢 Greedy Path
- Informasi heuristik dan hasil jalur di bawah graf

## Dependensi

- `tkinter` (bawaan Python)
- `networkx`
- `matplotlib`
- `heapq` (bawaan Python)

## Lisensi

Proyek ini bebas digunakan untuk keperluan pembelajaran dan penelitian.