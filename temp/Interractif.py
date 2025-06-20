import heapq
import networkx as nx
import matplotlib.pyplot as plt
import copy
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.patches as mpatches
from matplotlib.widgets import Button

# Pastikan matplotlib menggunakan backend yang kompatibel dengan TkAgg
import matplotlib
matplotlib.use('TkAgg')

# Menyimpan posisi tetap untuk node agar graph tidak berubah-ubah
pos = None
all_route_paths = []
selected_start = None
selected_end = None
G = None
fig = None
ax = None

def create_route_details_window(routes):
    """Membuat window baru untuk menampilkan detail rute"""
    if not routes:
        print("Tidak ada rute yang tersedia untuk ditampilkan")
        return
        
    details_window = tk.Toplevel()  # Gunakan Toplevel bukan Tk untuk mencegah konflik window
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

def on_node_click(event):
    global selected_start, selected_end, G, fig, ax
    
    print(f"Klik terdeteksi pada koordinat: ({event.xdata}, {event.ydata})")
    
    if event.xdata is None or event.ydata is None:
        print("Klik di luar area plot, abaikan")
        return
        
    # Temukan node terdekat dari klik
    clicked_node = None
    min_distance = float('inf')
    
    for node, (x, y) in pos.items():
        distance = ((event.xdata - x) ** 2 + (event.ydata - y) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            clicked_node = node
    
    # Jika klik cukup dekat dengan node
    if min_distance < 0.1:
        print(f"Node terdeteksi: {clicked_node}")
        if selected_start is None:
            selected_start = clicked_node
            # Ubah warna node start menjadi hijau
            nx.draw_networkx_nodes(G, pos, nodelist=[clicked_node], node_color='lightgreen', 
                                  node_size=1000, ax=ax)
            plt.title(f"Start: {clicked_node}, End: belum dipilih - Klik node lain untuk memilih tujuan")
            print(f"Node awal dipilih: {clicked_node}")
        elif selected_end is None and clicked_node != selected_start:
            selected_end = clicked_node
            # Ubah warna node end menjadi kuning
            nx.draw_networkx_nodes(G, pos, nodelist=[clicked_node], node_color='yellow', 
                                  node_size=1000, ax=ax)
            plt.title(f"Start: {selected_start}, End: {selected_end} - Klik 'Cari Rute' untuk melihat hasilnya")
            print(f"Node tujuan dipilih: {clicked_node}")
        # Refresh tampilan
        fig.canvas.draw()  # Pastikan menggunakan draw() bukan draw_idle()

def find_routes_callback(event):
    print("Tombol Cari Rute diklik")
    find_routes()

def find_routes():
    global selected_start, selected_end, fig
    
    print(f"Mencari rute dari {selected_start} ke {selected_end}")
    
    if selected_start and selected_end:
        plt.close(fig)  # Tutup figure saat ini
        
        # Temukan jalur alternatif
        all_paths = find_alternative_paths(graph, selected_start, selected_end, 4)
        
        # Tampilkan leaderboard
        print("\nLeaderboard Rute dari", selected_start, "ke", selected_end)
        print("-" * 50)
        for i, (path, distance) in enumerate(all_paths):
            if i < 4:  # Batasi maksimal 4 rute
                color_name = ['Merah', 'Biru', 'Hijau', 'Oranye'][i]
                route_path = " → ".join(path)
                print(f"Rute ke-{i+1} ({color_name}): {route_path}")
                print(f"Jarak: {distance}")
                print("-" * 50)
        
        # Tampilkan graph dengan semua rute (maksimal 4)
        draw_graph_with_routes(graph, all_paths[:4])
        
        # Reset pilihan untuk pencarian baru
        selected_start = None
        selected_end = None

def reset_selection_callback(event):
    print("Tombol Reset diklik")
    reset_selection()

def reset_selection():
    global selected_start, selected_end, G, fig, ax
    
    # Reset pilihan
    selected_start = None
    selected_end = None
    
    # Redraw graph dengan warna awal
    plt.clf()
    ax = plt.gca()
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightblue', ax=ax)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.title("Klik pada node untuk memilih gedung awal")
    
    # Refresh tampilan
    fig.canvas.draw()  # Gunakan draw() bukan draw_idle()

def draw_initial_graph(graph):
    global pos, G, fig, ax
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    G = nx.Graph()
    for node, edges in graph.items():
        for neighbor, weight in edges.items():
            G.add_edge(node, neighbor, weight=weight)
    
    if pos is None:
        pos = nx.spring_layout(G, seed=50)  # Posisi tetap dengan seed
    
    # Gambar graph
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightblue', ax=ax)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    
    plt.title("Klik pada node untuk memilih gedung awal")
    
    # Tambahkan tombol "Cari Rute" dan "Reset"
    plt.subplots_adjust(bottom=0.2)
    route_button_ax = plt.axes([0.7, 0.05, 0.15, 0.05])
    route_button = Button(route_button_ax, 'Cari Rute', color='lightgreen')
    route_button.on_clicked(find_routes_callback)  # Ganti dengan callback function
    
    reset_button_ax = plt.axes([0.5, 0.05, 0.15, 0.05])
    reset_button = Button(reset_button_ax, 'Reset Pilihan', color='lightcoral')
    reset_button.on_clicked(reset_selection_callback)  # Ganti dengan callback function
    
    # Tambahkan event handler untuk klik
    cid = fig.canvas.mpl_connect('button_press_event', on_node_click)
    print(f"Connection ID untuk event handler klik: {cid}")
    
    plt.show()

def view_details_callback(event):
    print("Tombol Lihat Detail diklik")
    create_route_details_window(all_route_paths)

def new_search_callback(event):
    print("Tombol Cari Rute Baru diklik")
    new_search()

def draw_graph_with_routes(graph, paths=None):
    global pos, all_route_paths, G, fig, ax
    
    # Simpan semua jalur untuk digunakan nanti
    if paths:
        all_route_paths = paths
    
    # Buat figure baru
    fig, ax = plt.subplots(figsize=(12, 8))
    
    G = nx.Graph()
    for node, edges in graph.items():
        for neighbor, weight in edges.items():
            G.add_edge(node, neighbor, weight=weight)
    
    if pos is None:
        pos = nx.spring_layout(G, seed=50)  # Posisi tetap dengan seed

    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightblue', ax=ax)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    # Warna untuk rute-rute (merah, biru, hijau, oranye)
    colors = ['red', 'blue', 'green', 'orange']
    
    # Untuk legend
    patches = []
    
    # Menampilkan rute dengan warna berbeda
    if paths:
        for i, (path, distance) in enumerate(paths):
            if i < len(colors):  # Maksimal 4 rute yang ditampilkan
                path_edges = list(zip(path, path[1:]))
                nx.draw_networkx_edges(G, pos, edgelist=path_edges, 
                                      edge_color=colors[i], width=2)
                
                # Tambahkan ke legend
                patch = mpatches.Patch(color=colors[i], 
                                     label=f"Rute ke-{i+1}: {distance}")
                patches.append(patch)
    
    plt.legend(handles=patches)
    
    # Tambahkan tombol "Lihat Detail" dan "Cari Rute Baru"
    plt.subplots_adjust(bottom=0.2)
    
    view_button_ax = plt.axes([0.7, 0.05, 0.15, 0.05])
    view_button = Button(view_button_ax, 'Lihat Detail', color='lightgray')
    view_button.on_clicked(view_details_callback)  # Ganti dengan callback function
    
    new_search_button_ax = plt.axes([0.5, 0.05, 0.15, 0.05])
    new_search_button = Button(new_search_button_ax, 'Cari Rute Baru', color='lightgreen')
    new_search_button.on_clicked(new_search_callback)  # Ganti dengan callback function
    
    plt.title(f"Rute dari {paths[0][0][0]} ke {paths[0][0][-1]}")
    plt.show()

def new_search():
    global fig
    plt.close(fig)  # Tutup figure saat ini
    draw_initial_graph(graph)  # Tampilkan graph awal lagi

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
    
    # Buat salinan graph untuk dimodifikasi
    temp_graph = copy.deepcopy(graph)
    
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
                        if v in temp_graph[u]:
                            edges_removed.append((u, v, temp_graph[u][v]))
                            temp_graph[u].pop(v)
                        if u in temp_graph[v]:
                            temp_graph[v].pop(u)
            
            # Hapus node di root_path (kecuali spur_node) sementara
            for node in root_path:
                if node != spur_node:
                    neighbors = list(temp_graph[node].keys())
                    for neighbor in neighbors:
                        edges_removed.append((node, neighbor, temp_graph[node][neighbor]))
                        temp_graph[node].pop(neighbor)
                        if node in temp_graph[neighbor]:
                            temp_graph[neighbor].pop(node)
            
            # Cari jalur dari spur_node ke end
            spur_path, spur_dist = dijkstra(temp_graph, spur_node, end)
            
            # Jika jalur ditemukan, gabungkan dengan root_path
            if spur_path:
                # Gabungkan root_path dengan spur_path tanpa duplikasi
                total_path = root_path[:-1] + spur_path
                
                # Hitung jarak total menggunakan graph asli
                total_dist = 0
                for i in range(len(total_path)-1):
                    u, v = total_path[i], total_path[i+1]
                    total_dist += graph[u][v]
                
                # Tambahkan ke kandidat jika belum ada
                candidate = (total_path, total_dist)
                if candidate not in B and candidate not in A:
                    B.append(candidate)
            
            # Kembalikan edge yang dihapus
            for u, v, weight in edges_removed:
                if u not in temp_graph:
                    temp_graph[u] = {}
                if v not in temp_graph:
                    temp_graph[v] = {}
                temp_graph[u][v] = weight
                temp_graph[v][u] = weight
        
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

# Tambahkan ini untuk pemeriksaan konfigurasi awal
def check_configuration():
    try:
        import sys
        print(f"Python version: {sys.version}")
        print(f"Matplotlib version: {matplotlib.__version__}")
        print(f"Matplotlib backend: {matplotlib.get_backend()}")
        print(f"Tkinter version: {tk.TkVersion}")
        print(f"NetworkX version: {nx.__version__}")
        
        # Periksa apakah Tkinter berfungsi
        root = tk.Tk()
        root.title("Test Tkinter")
        label = tk.Label(root, text="Tkinter berfungsi!")
        label.pack()
        root.after(2000, root.destroy)  # Tutup setelah 2 detik
        root.mainloop()
        print("Tkinter berfungsi dengan baik!")
        return True
    except Exception as e:
        print(f"Error saat memeriksa konfigurasi: {e}")
        return False

try:
    # Periksa konfigurasi dulu
    if check_configuration():
        # Tampilkan graph interaktif untuk pemilihan gedung awal dan akhir
        draw_initial_graph(graph)
    else:
        print("Ada masalah dengan konfigurasi. Silakan perbaiki terlebih dahulu.")
except Exception as e:
    print(f"Terjadi kesalahan: {e}")
    import traceback
    traceback.print_exc()  # Tampilkan traceback lengkap untuk debugging