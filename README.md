# Heuristic Search Visualization

Program GUI sederhana untuk memvisualisasikan dua algoritma pencarian terbimbing (*Heuristic Search*):  
- **Greedy Best First Search**
- **A\* (A-Star) Search**

Visualisasi dilakukan pada graf berbobot dengan nilai heuristik untuk memperkirakan jarak ke tujuan.

## Fitur

- Input node asal dan node tujuan
- Visualisasi graf dan jalur pencarian
- Menampilkan total cost dan jalur yang ditemukan oleh kedua algoritma
- Dibuat dengan Python, menggunakan `Tkinter` untuk GUI dan `matplotlib` + `networkx` untuk visualisasi

## Instalasi

Pastikan Python dan pip sudah terinstall. Lalu install dependency berikut:

```bash
pip install matplotlib networkx
```

## Menjalankan Program

```bash
python nama_file.py
```

> Ganti `nama_file.py` dengan nama file script kamu (misalnya `heuristic_search_gui.py`)

## Contoh

- Node Asal: `A`
- Node Tujuan: `G`

Program akan menampilkan hasil pencarian dan menandai jalur:
- **Hijau**: jalur dari Greedy Best First Search
- **Merah**: jalur dari A\* Search

## Struktur Graf

Graf didefinisikan secara manual dalam bentuk dictionary di kode, termasuk:
- **Bobot antar node**
- **Nilai heuristik**
- **Koordinat node untuk visualisasi**

## Screenshot

![demo](/assets/demo.png)

## Lisensi

Proyek ini bebas digunakan untuk pembelajaran dan pengembangan pribadi. 