import heapq
import networkx as nx
import matplotlib.pyplot as plt
import copy
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Menyimpan posisi tetap untuk node agar graph tidak berubah-ubah
pos = None
all_route_paths = []

def create_route_details_window(routes):
    """Membuat window baru untuk menampilkan detail rute"""
    details_window = tk.Tk()
    details_window.title("Detail Rute")
    details_window.geometry("500x400")
    
    # Membuat notebook (tabbed interface)
    notebook = ttk.Notebook(details_window)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Warna untuk setiap rute
    colors = ['red', 'blue', 'green', 'orange']
    
    # Membuat tab untuk setiap rute
    for i, (path, distance) in enumerate(routes):
        if i >= 4:  # Maksimal 4 rute
            break
            
        # Membuat frame untuk tab
        tab = ttk.Frame(notebook)
        color_name = ['Merah', 'Biru', 'Hijau', 'Oranye'][i]
        notebook.add(tab, text=f"Rute {i+1} ({color_name})")
        
        # Informasi rute
        route_info = tk.Label(tab, 
                           text=f"Rute {i+1}: {' → '.join(path)}\nJarak total: {distance}",
                           justify=tk.LEFT, 
                           padx=10, 
                           pady=10,
                           wraplength=450)
        route_info.pack(fill='both')
        
        # Detail langkah per langkah
        steps_frame = ttk.LabelFrame(tab, text="Langkah-langkah")
        steps_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        steps_text = tk.Text(steps_frame, height=10, width=50)
        steps_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tambahkan scrollbar jika teks terlalu panjang
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
    
    details_window.mainloop()

def draw_graph(graph, paths=None):
    global pos, all_route_paths
    
    # Simpan semua jalur untuk digunakan nanti
    if paths:
        all_route_paths = paths
    
    # Buat figure baru
    plt.figure(figsize=(12, 8))
    
    G = nx.Graph()
    for node, edges in graph.items():
        for neighbor, weight in edges.items():
            G.add_edge(node, neighbor, weight=weight)
    
    if pos is None:
        pos = nx.spring_layout(G, seed=50)  # Posisi tetap dengan seed

    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightblue')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    # Warna untuk rute-rute (merah, biru, hijau, oranye)
    colors = ['red', 'blue', 'green', 'orange']
    
    # Menampilkan rute dengan warna berbeda
    if paths:
        for i, (path, distance) in enumerate(paths):
            if i < len(colors):  # Maksimal 4 rute yang ditampilkan
                path_edges = list(zip(path, path[1:]))
                nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                                      edge_color=colors[i], width=2, 
                                      label=f"Rute ke-{i+1}: {distance}")
    
    # Tambahkan tombol "Lihat Detail" pada legend
    ax = plt.gca()
    plt.subplots_adjust(bottom=0.2)
    view_button_ax = plt.axes([0.81, 0.05, 0.1, 0.05])
    view_button = plt.Button(view_button_ax, 'Lihat Detail', color='lightgray')
    view_button.on_clicked(lambda event: create_route_details_window(all_route_paths))
    
    plt.legend()
    plt.show()

def find_path_with_intermediate(graph, start, intermediate, end, k=4):
    """
    Menemukan k jalur alternatif dari start ke end melalui gedung intermediate
    """
    # Cari jalur dari start ke intermediate
    paths_to_intermediate = find_alternative_paths(graph, start, intermediate, k)
    
    # Cari jalur dari intermediate ke end
    paths_from_intermediate = find_alternative_paths(graph, intermediate, end, k)
    
    # Gabungkan jalur
    combined_paths = []
    
    for path1, dist1 in paths_to_intermediate:
        for path2, dist2 in paths_from_intermediate:
            # Gabungkan path tanpa mengulangi node intermediate
            # path1: [start, ..., intermediate]
            # path2: [intermediate, ..., end]
            combined_path = path1 + path2[1:]  # Skip node intermediate dari path kedua
            combined_dist = dist1 + dist2
            
            combined_paths.append((combined_path, combined_dist))
    
    # Urutkan berdasarkan jarak total
    combined_paths.sort(key=lambda x: x[1])
    
    # Ambil k jalur terbaik
    return combined_paths[:k]

def find_alternative_paths(graph, start, end, k=4):
    """
    Menemukan k jalur alternatif dari start ke end
    """
    # Mencari jalur utama dengan Dijkstra
    original_path, original_distance = dijkstra(graph, start, end)
    
    all_paths = [(original_path, original_distance)]
    
    # Jika hanya ingin 1 jalur, kembalikan hasil
    if k <= 1 or not original_path:
        return all_paths
    
    # Mencari semua jalur unik dengan Yen's k-shortest path algorithm
    # Implementasi sederhana dari algoritma Yen
    A = [(original_path, original_distance)]  # Jalur terpendek yang ditemukan
    B = []  # Kandidat jalur
    
    # Cari k-1 jalur alternatif
    for i in range(1, k):
        # Jalur terakhir yang ditemukan
        prev_path = A[-1][0]
        
        # Coba tiap node sebagai titik percabangan
        for j in range(len(prev_path) - 1):
            spur_node = prev_path[j]
            root_path = prev_path[:j+1]
            
            # Simpan edge yang akan dihapus sementara
            edges_removed = []
            
            # Hapus edge yang digunakan oleh jalur sebelumnya dengan root_path yang sama
            for path, dist in A:
                if len(path) > j and path[:j+1] == root_path:
                    if j+1 < len(path):
                        u = path[j]
                        v = path[j+1]
                        if v in graph[u]:
                            edges_removed.append((u, v, graph[u][v]))
                            graph[u].pop(v)
                        if u in graph[v]:
                            graph[v].pop(u)
            
            # Hapus node di root_path (kecuali spur_node) sementara
            for node in root_path:
                if node != spur_node:
                    neighbors = list(graph[node].keys())
                    for neighbor in neighbors:
                        edges_removed.append((node, neighbor, graph[node][neighbor]))
                        graph[node].pop(neighbor)
                        if node in graph[neighbor]:
                            graph[neighbor].pop(node)
            
            # Cari jalur dari spur_node ke end
            spur_path, spur_dist = dijkstra(graph, spur_node, end)
            
            # Jika jalur ditemukan, gabungkan dengan root_path
            if spur_path:
                # Gabungkan root_path dengan spur_path tanpa duplikasi
                total_path = root_path[:-1] + spur_path
                
                # Hitung jarak total
                total_dist = 0
                for i in range(len(total_path)-1):
                    u, v = total_path[i], total_path[i+1]
                    # Periksa apakah edge dihapus
                    edge_found = False
                    for edge in edges_removed:
                        if (edge[0] == u and edge[1] == v) or (edge[0] == v and edge[1] == u):
                            total_dist += edge[2]
                            edge_found = True
                            break
                    # Jika edge tidak dihapus, ambil dari graph
                    if not edge_found and v in graph.get(u, {}):
                        total_dist += graph[u][v]
                
                # Tambahkan ke kandidat jika belum ada
                candidate = (total_path, total_dist)
                if candidate not in B and candidate not in A:
                    B.append(candidate)
            
            # Kembalikan edge yang dihapus
            for u, v, weight in edges_removed:
                if u not in graph:
                    graph[u] = {}
                if v not in graph:
                    graph[v] = {}
                graph[u][v] = weight
                graph[v][u] = weight
        
        if not B:
            # Tidak ada jalur alternatif lagi
            break
        
        # Pilih jalur terpendek dari kandidat
        B.sort(key=lambda x: x[1])
        A.append(B[0])
        B.pop(0)
    
    return A

def dijkstra(graph, start, end):
    pq = [(0, start)]
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous_nodes = {node: None for node in graph}
    paths = {node: [] for node in graph}
    paths[start] = [start]
    
    while pq:
        current_distance, current_node = heapq.heappop(pq)
        
        if current_node == end:
            break
        
        if current_distance > distances[current_node]:
            continue
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                paths[neighbor] = paths[current_node] + [neighbor]
                heapq.heappush(pq, (distance, neighbor))
    
    if end not in paths or not paths[end]:
        return [], float('inf')
    return paths[end], distances[end]

def create_input_interface():
    """Membuat UI untuk input rute dan mampir"""
    root = tk.Tk()
    root.title("Pencarian Rute Kampus")
    root.geometry("400x300")
    
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Label dan input untuk gedung awal
    ttk.Label(frame, text="Gedung Awal:").grid(column=0, row=0, sticky=tk.W, pady=5)
    start_var = tk.StringVar()
    start_entry = ttk.Entry(frame, width=15, textvariable=start_var)
    start_entry.grid(column=1, row=0, sticky=tk.W, pady=5)
    
    # Label dan input untuk gedung tujuan
    ttk.Label(frame, text="Gedung Tujuan:").grid(column=0, row=1, sticky=tk.W, pady=5)
    end_var = tk.StringVar()
    end_entry = ttk.Entry(frame, width=15, textvariable=end_var)
    end_entry.grid(column=1, row=1, sticky=tk.W, pady=5)
    
    # Pilihan untuk mampir
    via_var = tk.BooleanVar()
    via_var.set(False)
    via_check = ttk.Checkbutton(frame, text="Mampir ke gedung lain?", variable=via_var, 
                               command=lambda: toggle_via_input(via_var.get(), via_frame))
    via_check.grid(column=0, row=2, columnspan=2, sticky=tk.W, pady=5)
    
    # Frame untuk input gedung mampir (awalnya disembunyikan)
    via_frame = ttk.Frame(frame)
    via_frame.grid(column=0, row=3, columnspan=2, sticky=tk.W, pady=5)
    via_frame.grid_remove()  # Sembunyikan awalnya
    
    ttk.Label(via_frame, text="Gedung Mampir:").grid(column=0, row=0, sticky=tk.W)
    via_node_var = tk.StringVar()
    via_entry = ttk.Entry(via_frame, width=15, textvariable=via_node_var)
    via_entry.grid(column=1, row=0, sticky=tk.W)
    
    # Tombol Cari Rute
    ttk.Button(frame, text="Cari Rute", 
              command=lambda: find_route(start_var.get(), end_var.get(), 
                                        via_var.get(), via_node_var.get(), root)).grid(
        column=0, row=4, columnspan=2, pady=20)
    
    root.mainloop()

def toggle_via_input(show, via_frame):
    """Menampilkan atau menyembunyikan input gedung mampir"""
    if show:
        via_frame.grid()
    else:
        via_frame.grid_remove()

def find_route(start, end, use_via, via_node, root):
    """Mencari rute dan menampilkan hasil"""
    if not start or not end:
        messagebox.showerror("Error", "Gedung awal dan tujuan harus diisi!")
        return
    
    if start not in graph or end not in graph:
        messagebox.showerror("Error", "Gedung tidak ditemukan dalam graph!")
        return
    
    if use_via:
        if not via_node:
            messagebox.showerror("Error", "Gedung mampir harus diisi!")
            return
        if via_node not in graph:
            messagebox.showerror("Error", "Gedung mampir tidak ditemukan dalam graph!")
            return
        
        all_paths = find_path_with_intermediate(graph, start, via_node, end, 4)
        root.destroy()  # Tutup window input
        
        # Tampilkan leaderboard
        print("\nLeaderboard Rute dari", start, "ke", end, "melalui", via_node)
    else:
        all_paths = find_alternative_paths(graph, start, end, 4)
        root.destroy()  # Tutup window input
        
        # Tampilkan leaderboard
        print("\nLeaderboard Rute dari", start, "ke", end)
    
    print("-" * 50)
    for i, (path, distance) in enumerate(all_paths):
        if i < 4:  # Batasi maksimal 4 rute
            color_name = ['Merah', 'Biru', 'Hijau', 'Oranye'][i]
            route_path = " → ".join(path)
            print(f"Rute ke-{i+1} ({color_name}): {route_path}")
            print(f"Jarak: {distance}")
            print("-" * 50)
    
    # Tampilkan graph dengan semua rute (maksimal 4)
    draw_graph(graph, all_paths[:4])

# Input user
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

# Tampilkan graph asli
draw_graph(graph)

# Jalankan antarmuka input
create_input_interface()