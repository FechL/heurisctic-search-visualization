import heapq
import networkx as nx
import matplotlib.pyplot as plt
import copy
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

# Menyimpan posisi tetap untuk node agar graph tidak berubah-ubah
pos = None
all_route_paths = []

# Kamus untuk menyimpan koordinat setiap node (untuk heuristik)
# Format: {node: (x, y)}
node_coordinates = {}

# Inisialisasi graph
graph = {
    "G1": {"G2": 4, "G3": 2},
    "G2": {"G1": 4, "G4": 5, "G5": 6},
    "G3": {"G1": 2, "G6": 3, "G7": 4},
    "G4": {"G2": 5, "G8": 7, "G9": 3},
    "G5": {"G2": 6, "G10": 8, "G11": 5},
    "G6": {"G3": 3, "G12": 4, "G13": 6},
    "G7": {"G3": 4, "G14": 5, "G15": 7},
    "G8": {"G4": 7, "G16": 3, "G17": 8},
    "G9": {"G4": 3, "G18": 5, "G19": 6},
    "G10": {"G5": 8, "G20": 4, "G21": 7},
    "G11": {"G5": 5, "G22": 6, "G23": 3},
    "G12": {"G6": 4, "G24": 7, "G25": 5},
    "G13": {"G6": 6, "G26": 4, "G27": 3},
    "G14": {"G7": 5, "G28": 6, "G29": 4},
    "G15": {"G7": 7, "G30": 8},
    "G16": {"G8": 3, "G17": 5},
    "G17": {"G8": 8, "G18": 6},
    "G18": {"G9": 5, "G19": 4},
    "G19": {"G9": 6, "G20": 3},
    "G20": {"G10": 4, "G21": 7},
    "G21": {"G10": 7, "G22": 5},
    "G22": {"G11": 6, "G23": 4},
    "G23": {"G11": 3, "G24": 6},
    "G24": {"G12": 7, "G25": 5},
    "G25": {"G12": 5, "G26": 4},
    "G26": {"G13": 4, "G27": 3},
    "G27": {"G13": 3, "G28": 6},
    "G28": {"G14": 6, "G29": 4},
    "G29": {"G14": 4, "G30": 8},
    "G30": {"G15": 8}
}

# Nilai heuristik untuk setiap node (jarak estimasi ke G30)
heuristic = {
    "G1": 25, "G2": 24, "G3": 23, "G4": 22, "G5": 21, "G6": 20, "G7": 19,
    "G8": 18, "G9": 17, "G10": 16, "G11": 15, "G12": 14, "G13": 13, "G14": 12,
    "G15": 11, "G16": 10, "G17": 9, "G18": 8, "G19": 7, "G20": 6, "G21": 5,
    "G22": 4, "G23": 3, "G24": 2, "G25": 2, "G26": 2, "G27": 1, "G28": 1,
    "G29": 1, "G30": 0
}

def get_heuristic(node, end):
    """Mendapatkan nilai heuristik antara node dan end"""
    # Jika end adalah G30, gunakan nilai heuristik yang sudah didefinisikan
    if end == "G30":
        return heuristic.get(node, 0)
    else:
        # Gunakan jarak euclidean jika tidak menuju G30
        return euclidean_distance(node, end)

def euclidean_distance(node1, node2):
    """Menghitung jarak Euclidean antara dua node"""
    if node1 in node_coordinates and node2 in node_coordinates:
        x1, y1 = node_coordinates[node1]
        x2, y2 = node_coordinates[node2]
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return 0  # Default jika koordinat tidak tersedia

def simple_hill_climbing(graph, start, end):
    """Pencarian rute dengan Simple Hill Climbing"""
    current = start
    path = [current]
    total_distance = 0
    
    while current != end:
        neighbors = graph[current]
        if not neighbors:
            return [], float('inf')  # No path found
        
        # Cari neighbor dengan jarak heuristik terkecil ke tujuan
        best_neighbor = None
        best_score = float('inf')
        
        for neighbor, weight in neighbors.items():
            if neighbor in path:  # Hindari loop
                continue
                
            # Heuristik: jarak langsung (euclidean) ke tujuan
            h = get_heuristic(neighbor, end)
            
            if h < best_score:
                best_score = h
                best_neighbor = neighbor
        
        if best_neighbor is None:
            # Tidak ada tetangga yang lebih baik (lokal minimum)
            return [], float('inf')  # No path found
        
        # Lanjut ke neighbor terbaik
        total_distance += graph[current][best_neighbor]
        current = best_neighbor
        path.append(current)
    
    # Hitung total jarak
    total_dist = 0
    for i in range(len(path)-1):
        total_dist += graph[path[i]][path[i+1]]
    
    return path, total_dist

def steepest_ascent_hill_climbing(graph, start, end):
    """Pencarian rute dengan Steepest Ascent Hill Climbing"""
    current = start
    path = [current]
    total_distance = 0
    visited = set([current])
    
    while current != end:
        if not graph[current]:
            return [], float('inf')  # No path found
        
        # Evaluasi semua tetangga terlebih dahulu
        candidates = []
        
        for neighbor, weight in graph[current].items():
            if neighbor not in visited:  # Hindari loop
                h = get_heuristic(neighbor, end)
                candidates.append((h, neighbor, weight))
        
        if not candidates:
            # Tidak ada tetangga yang belum dikunjungi (lokal minimum)
            return [], float('inf') 
        
        # Pilih tetangga dengan nilai heuristik terbaik (nilai terkecil)
        candidates.sort()  # Urutkan berdasarkan nilai heuristik
        _, best_neighbor, weight = candidates[0]
        
        # Lanjut ke neighbor terbaik
        total_distance += weight
        current = best_neighbor
        path.append(current)
        visited.add(current)
    
    return path, total_distance

def a_star_search(graph, start, end):
    """Pencarian rute dengan A* Search"""
    # Antrian prioritas berisi (f_score, node, path, total_dist)
    open_set = [(get_heuristic(start, end), start, [start], 0)]
    closed_set = set()
    
    while open_set:
        # Ambil node dengan f_score terendah
        f, current, path, dist = heapq.heappop(open_set)
        
        if current == end:
            return path, dist
            
        if current in closed_set:
            continue
            
        closed_set.add(current)
        
        for neighbor, weight in graph[current].items():
            if neighbor in closed_set:
                continue
                
            # g_score adalah jarak dari start ke neighbor via current
            g_score = dist + weight
            # h_score adalah estimasi jarak dari neighbor ke end
            h_score = get_heuristic(neighbor, end)
            # f_score adalah total estimasi jarak
            f_score = g_score + h_score
            
            # Tambahkan ke open set
            new_path = path + [neighbor]
            heapq.heappush(open_set, (f_score, neighbor, new_path, g_score))
    
    return [], float('inf')  # No path found

def greedy_search(graph, start, end):
    """Pencarian rute dengan Greedy Best-First Search"""
    # Antrian prioritas berisi (heuristic, node, path, total_dist)
    open_set = [(get_heuristic(start, end), start, [start], 0)]
    closed_set = set()
    
    while open_set:
        # Ambil node dengan heuristik terendah
        h, current, path, dist = heapq.heappop(open_set)
        
        if current == end:
            return path, dist
            
        if current in closed_set:
            continue
            
        closed_set.add(current)
        
        for neighbor, weight in graph[current].items():
            if neighbor in closed_set:
                continue
                
            # Hanya gunakan heuristik (tanpa g_score) untuk greedy
            h_score = get_heuristic(neighbor, end)
            
            # Tambahkan ke open set
            new_path = path + [neighbor]
            new_dist = dist + weight
            heapq.heappush(open_set, (h_score, neighbor, new_path, new_dist))
    
    return [], float('inf')  # No path found

def create_route_details_window(algorithm_results):
    """Membuat window baru untuk menampilkan detail rute dari semua algoritma"""
    details_window = tk.Toplevel()
    details_window.title("Perbandingan Algoritma Pencarian Rute")
    details_window.geometry("700x600")
    
    # Membuat notebook (tabbed interface)
    notebook = ttk.Notebook(details_window)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Membuat tab untuk setiap algoritma
    algorithms = ['Simple Hill Climbing', 'Steepest Ascent Hill Climbing', 'A* Search', 'Greedy Search']
    colors = ['red', 'orange', 'blue', 'green']
    
    for i, algo_name in enumerate(algorithms):
        # Ambil hasil dari algoritma
        path, distance = algorithm_results[i]
        
        # Membuat frame untuk tab
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=f"{algo_name}")
        
        # Bagian atas: ringkasan rute
        summary_frame = ttk.LabelFrame(tab, text="Ringkasan Rute")
        summary_frame.pack(fill='x', padx=10, pady=10)
        
        # Jika rute ditemukan
        if path and distance != float('inf'):
            route_info = tk.Label(summary_frame, 
                               text=f"Algoritma: {algo_name}\nRute: {' → '.join(path)}\nJarak total: {distance}",
                               justify=tk.LEFT, 
                               padx=10, 
                               pady=10,
                               wraplength=650)
        else:
            route_info = tk.Label(summary_frame, 
                               text=f"Algoritma: {algo_name}\nTidak ditemukan rute dari titik awal ke tujuan.",
                               justify=tk.LEFT, 
                               padx=10, 
                               pady=10,
                               wraplength=650)
        route_info.pack(fill='x')
        
        # Bagian bawah: detail langkah-langkah
        if path and distance != float('inf'):
            steps_frame = ttk.LabelFrame(tab, text="Langkah-langkah Rute")
            steps_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            steps_text = tk.Text(steps_frame, height=15, width=60)
            steps_text.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Tambahkan scrollbar
            scrollbar = tk.Scrollbar(steps_text)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            steps_text.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=steps_text.yview)
            
            # Isi detail langkah
            total_dist = 0
            for j in range(len(path)-1):
                from_node = path[j]
                to_node = path[j+1]
                edge_dist = graph[from_node][to_node]
                total_dist += edge_dist
                steps_text.insert(tk.END, f"Langkah {j+1}: Dari {from_node} ke {to_node} ({edge_dist} unit)\n")
            
            steps_text.insert(tk.END, f"\nTotal jarak: {distance} unit")
            steps_text.config(state=tk.DISABLED)  # Jadikan read-only
        
        # Bagian penjelasan algoritma
        explanation_frame = ttk.LabelFrame(tab, text="Penjelasan Algoritma")
        explanation_frame.pack(fill='x', padx=10, pady=10)
        
        if algo_name == 'Simple Hill Climbing':
            explanation = (
                "Simple Hill Climbing adalah algoritma pencarian lokal yang selalu bergerak ke arah yang lebih baik. "
                "Algoritma ini memilih tetangga dengan nilai heuristik terbaik (jarak terdekat ke tujuan) "
                "tanpa mempertimbangkan jarak yang sudah ditempuh. Hill Climbing rentan terjebak di optimum lokal."
            )
        elif algo_name == 'Steepest Ascent Hill Climbing':
            explanation = (
                "Steepest Ascent Hill Climbing adalah variasi dari Hill Climbing yang mengecek semua tetangga "
                "terlebih dahulu sebelum memilih yang terbaik. Algoritma ini memilih node dengan nilai heuristik terkecil "
                "dari semua tetangga yang tersedia. Lebih optimal dari Simple Hill Climbing namun masih bisa terjebak di optimum lokal."
            )
        elif algo_name == 'A* Search':
            explanation = (
                "A* Search adalah algoritma pencarian terinformasi yang menggabungkan jarak sebenarnya (g) "
                "dan estimasi jarak ke tujuan (h). A* memilih node dengan nilai f = g + h terendah. "
                "A* menjamin menemukan jalur terpendek jika heuristik yang digunakan tidak overestimasi."
            )
        else:  # Greedy
            explanation = (
                "Greedy Best-First Search adalah algoritma pencarian terinformasi yang hanya mempertimbangkan "
                "estimasi jarak ke tujuan (heuristik). Algoritma ini memilih node yang terlihat paling dekat "
                "dengan tujuan. Greedy dapat menemukan jalur dengan cepat, tetapi tidak menjamin jalur terpendek."
            )
        
        explanation_text = tk.Label(explanation_frame,
                                 text=explanation,
                                 justify=tk.LEFT,
                                 wraplength=650,
                                 padx=10,
                                 pady=10)
        explanation_text.pack(fill='x')
    
    details_window.mainloop()

def draw_graph(graph, algorithm_results=None):
    global pos, all_route_paths, node_coordinates
    
    # Buat figure baru
    plt.figure(figsize=(12, 8))
    
    G = nx.Graph()
    for node, edges in graph.items():
        for neighbor, weight in edges.items():
            G.add_edge(node, neighbor, weight=weight)
    
    if pos is None:
        pos = nx.spring_layout(G, seed=50)  # Posisi tetap dengan seed
        # Simpan koordinat node untuk heuristik
        for node, (x, y) in pos.items():
            node_coordinates[node] = (x, y)
    
    # Gambar graph dasar
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightblue')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    
    # Warna untuk rute-rute dari algoritma yang berbeda
    colors = ['red', 'orange', 'blue', 'green']
    
    # Menampilkan rute dari masing-masing algoritma
    if algorithm_results:
        # Buat legend label
        algorithm_names = ['Simple Hill Climbing', 'Steepest Ascent Hill Climbing', 'A* Search', 'Greedy Search']
        
        for i, (path, distance) in enumerate(algorithm_results):
            if i < len(colors) and path:  # Jika rute ditemukan
                path_edges = list(zip(path, path[1:]))
                nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                                      edge_color=colors[i], width=2+i, 
                                      label=f"{algorithm_names[i]}: {distance}")
    
    # Tambahkan tombol "Lihat Detail" pada legend
    if algorithm_results:
        ax = plt.gca()
        plt.subplots_adjust(bottom=0.2)
        view_button_ax = plt.axes([0.81, 0.05, 0.1, 0.05])
        view_button = plt.Button(view_button_ax, 'Lihat Detail', color='lightgray')
        view_button.on_clicked(lambda event: create_route_details_window(algorithm_results))
    
    plt.legend()
    plt.title('Perbandingan Algoritma Pencarian Rute')
    plt.tight_layout()
    plt.show()

def create_input_interface():
    """Membuat UI untuk input rute"""
    root = tk.Tk()
    root.title("Pencarian Rute dengan Algoritma Heuristik")
    root.geometry("400x300")
    
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Label dan input untuk gedung awal
    ttk.Label(frame, text="Kota Asal:").grid(column=0, row=0, sticky=tk.W, pady=5)
    start_var = tk.StringVar()
    start_entry = ttk.Combobox(frame, width=15, textvariable=start_var)
    start_entry['values'] = list(graph.keys())
    start_entry.grid(column=1, row=0, sticky=tk.W, pady=5)
    
    # Label dan input untuk gedung tujuan
    ttk.Label(frame, text="Kota Tujuan:").grid(column=0, row=1, sticky=tk.W, pady=5)
    end_var = tk.StringVar()
    end_entry = ttk.Combobox(frame, width=15, textvariable=end_var)
    end_entry['values'] = list(graph.keys())
    end_entry.grid(column=1, row=1, sticky=tk.W, pady=5)
    
    # Tombol Cari Rute
    ttk.Button(frame, text="Bandingkan Algoritma", 
              command=lambda: compare_algorithms(start_var.get(), end_var.get(), root)).grid(
        column=0, row=4, columnspan=2, pady=20)
    
    # Informasi tambahan
    info_text = "Program akan mencari rute menggunakan:\n" \
                "- Simple Hill Climbing\n" \
                "- Steepest Ascent Hill Climbing\n" \
                "- A* Search\n" \
                "- Greedy Best-First Search"
    info_label = ttk.Label(frame, text=info_text, justify=tk.LEFT)
    info_label.grid(column=0, row=5, columnspan=2, sticky=tk.W, pady=10)
    
    root.mainloop()

def compare_algorithms(start, end, root):
    """Mencari rute dengan 4 algoritma berbeda dan menampilkan hasilnya"""
    if not start or not end:
        messagebox.showerror("Error", "Kota asal dan tujuan harus diisi!")
        return
    
    if start not in graph or end not in graph:
        messagebox.showerror("Error", "Kota tidak ditemukan dalam graph!")
        return
    
    # Jalankan keempat algoritma
    simple_hill_climbing_result = simple_hill_climbing(graph, start, end)
    steepest_hill_climbing_result = steepest_ascent_hill_climbing(graph, start, end)
    a_star_result = a_star_search(graph, start, end)
    greedy_result = greedy_search(graph, start, end)
    
    # Kumpulkan hasil
    algorithm_results = [simple_hill_climbing_result, steepest_hill_climbing_result, a_star_result, greedy_result]
    
    # Tampilkan leaderboard di konsol
    algorithm_names = ['Simple Hill Climbing', 'Steepest Ascent Hill Climbing', 'A* Search', 'Greedy Best-First Search']
    
    print("\nPerbandingan Algoritma Pencarian Rute dari", start, "ke", end)
    print("-" * 60)
    
    for i, ((path, distance), algo_name) in enumerate(zip(algorithm_results, algorithm_names)):
        if path and distance != float('inf'):
            route_path = " → ".join(path)
            print(f"{algo_name}:")
            print(f"Rute: {route_path}")
            print(f"Jarak: {distance}")
        else:
            print(f"{algo_name}: Tidak menemukan rute")
        print("-" * 60)
    
    # Tampilkan graph dengan semua rute
    draw_graph(graph, algorithm_results)
    
    root.destroy()  # Tutup window input

# Menghitung koordinat node untuk heuristik
G_temp = nx.Graph()
for node, edges in graph.items():
    for neighbor, weight in edges.items():
        G_temp.add_edge(node, neighbor, weight=weight)
        
pos = nx.spring_layout(G_temp, seed=50)
for node, (x, y) in pos.items():
    node_coordinates[node] = (x, y)

# Jalankan program
if __name__ == "__main__":
    # Tampilkan graph asli
    draw_graph(graph)
    
    # Jalankan antarmuka input
    create_input_interface()