"""
Program Algoritma Pencarian Terbimbing (Heuristic Search) dengan GUI
Menggunakan heuristik berdasarkan jarak antar node
"""

import tkinter as tk
from tkinter import ttk, messagebox
import heapq
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Graph berisi node dan bobot antar node
graph = {
    "A": {"B": 2, "C": 3},
    "B": {"A": 2, "D": 4, "E": 5},
    "C": {"A": 3, "E": 1, "G": 7},
    "D": {"B": 4, "F": 6},
    "E": {"B": 5, "C": 1, "F": 2},
    "F": {"D": 6, "E": 2, "G": 2},
    "G": {"C": 7, "F": 2}
}

# Posisi node untuk visualisasi
node_positions = {
    "A": (0, 2),
    "B": (1, 3),
    "C": (1, 1),
    "D": (2, 4),
    "E": (2, 2),
    "F": (3, 3),
    "G": (4, 2)
}

def calculate_heuristic(graph, goal):
    """
    Menghitung nilai heuristik berdasarkan jarak terpendek ke node tujuan
    menggunakan algoritma Dijkstra
    """
    heuristic = {node: float('inf') for node in graph}
    heuristic[goal] = 0
    
    # Menggunakan Dijkstra untuk menghitung jarak terpendek
    queue = [(0, goal)]  # (distance, node)
    visited = set()
    
    while queue and len(visited) < len(graph):
        current_distance, current_node = heapq.heappop(queue)
        
        if current_node in visited:
            continue
            
        visited.add(current_node)
        
        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < heuristic[neighbor]:
                heuristic[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))
    
    return heuristic

def greedy_best_first_search(graph, start, goal, heuristic):
    """
    Greedy Best First Search: 
    Selalu mengambil node dengan nilai heuristik terendah.
    Strategi ini hanya mempertimbangkan jarak perkiraan ke tujuan,
    tanpa memperhitungkan biaya perjalanan sejauh ini.
    """
    
    # Priority queue dengan (nilai_heuristik, node, path, cost)
    open_list = [(heuristic[start], start, [start], 0)]
    closed_set = set()
    
    while open_list:
        # Ambil node dengan nilai heuristik terendah
        h, current, path, cost = heapq.heappop(open_list)
        
        # Jika sudah sampai tujuan
        if current == goal:
            return path, cost
        
        # Skip jika sudah diproses
        if current in closed_set:
            continue
            
        closed_set.add(current)
        
        # Periksa semua tetangga
        for neighbor, step_cost in graph[current].items():
            if neighbor not in closed_set:
                new_path = path + [neighbor]
                new_cost = cost + step_cost
                # Dalam Greedy, kita hanya memperhitungkan nilai heuristik
                heapq.heappush(open_list, (heuristic[neighbor], neighbor, new_path, new_cost))
    
    return None, None  # Tidak ditemukan jalur

def a_star_search(graph, start, goal, heuristic):
    """
    A* Search: 
    Mengambil node dengan nilai f(n) = g(n) + h(n) terendah.
    g(n) adalah biaya dari start ke node saat ini
    h(n) adalah nilai heuristik (perkiraan biaya) dari node saat ini ke tujuan
    A* menyeimbangkan antara biaya sejauh ini dan perkiraan biaya ke tujuan
    """
    
    # Priority queue dengan (f_score, node, path, cost)
    open_list = [(heuristic[start], start, [start], 0)]
    closed_set = set()
    
    while open_list:
        # Ambil node dengan nilai f_score terendah
        f, current, path, cost = heapq.heappop(open_list)
        
        # Jika sudah sampai tujuan
        if current == goal:
            return path, cost
        
        # Skip jika sudah diproses
        if current in closed_set:
            continue
            
        closed_set.add(current)
        
        # Periksa semua tetangga
        for neighbor, step_cost in graph[current].items():
            if neighbor not in closed_set:
                new_path = path + [neighbor]
                new_cost = cost + step_cost
                # Dalam A*, f(n) = g(n) + h(n)
                f_score = new_cost + heuristic[neighbor]
                heapq.heappush(open_list, (f_score, neighbor, new_path, new_cost))
    
    return None, None  # Tidak ditemukan jalur

class HeuristicSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Algoritma Pencarian Terbimbing")
        self.root.geometry("800x600")
        
        # Nilai heuristik awal (diinisialisasi di awal)
        self.heuristic = {node: 0 for node in graph}
        
        # Frame utama
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame untuk input
        input_frame = ttk.LabelFrame(main_frame, text="Input", padding=10)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Node asal dan tujuan
        ttk.Label(input_frame, text="Node Asal:").grid(row=0, column=0, padx=5, pady=5)
        self.start_var = tk.StringVar()
        start_combo = ttk.Combobox(input_frame, textvariable=self.start_var, values=sorted(graph.keys()), width=5)
        start_combo.grid(row=0, column=1, padx=5, pady=5)
        start_combo.current(0)
        
        ttk.Label(input_frame, text="Node Tujuan:").grid(row=0, column=2, padx=5, pady=5)
        self.goal_var = tk.StringVar()
        goal_combo = ttk.Combobox(input_frame, textvariable=self.goal_var, values=sorted(graph.keys()), width=5)
        goal_combo.grid(row=0, column=3, padx=5, pady=5)
        goal_combo.current(6)  # Default ke G
        
        # Hitung heuristik awal untuk tujuan default (G)
        self.heuristic = calculate_heuristic(graph, "G")
        
        # Tombol cari
        search_button = ttk.Button(input_frame, text="Cari Rute", command=self.search_routes)
        search_button.grid(row=0, column=4, padx=20, pady=5)
        
        # Frame untuk visualisasi graf
        self.graph_frame = ttk.LabelFrame(main_frame, text="Visualisasi Graf", padding=10)
        self.graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame untuk hasil
        self.result_frame = ttk.LabelFrame(main_frame, text="Hasil Pencarian", padding=10)
        self.result_frame.pack(fill=tk.X, pady=10)
        
        # Text widget untuk menampilkan hasil
        self.result_text = tk.Text(self.result_frame, height=10, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Tampilkan graf awal
        self.draw_graph()
    
    def draw_graph(self, greedy_path=None, astar_path=None):
        # Bersihkan frame graf
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Buat graf menggunakan networkx
        G = nx.Graph()
        
        # Tambahkan node dan edge
        for node in graph:
            G.add_node(node)
            for neighbor, weight in graph[node].items():
                G.add_edge(node, neighbor, weight=weight)
        
        # Buat figure matplotlib
        fig, ax = plt.subplots(figsize=(6, 4))
        
        # Gambar node dan edge
        nx.draw_networkx_nodes(G, node_positions, node_color='lightblue', node_size=500)
        
        # Label node
        node_labels = {}
        for node in graph:
            node_labels[node] = f"{node} (h={self.heuristic[node]})"
        
        nx.draw_networkx_labels(G, node_positions, labels=node_labels)
        
        # Edge dan labelnya
        edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edges(G, node_positions)
        nx.draw_networkx_edge_labels(G, node_positions, edge_labels=edge_labels)
        
        # Gambar jalur Greedy jika ada
        if greedy_path and len(greedy_path) > 1:
            greedy_edges = [(greedy_path[i], greedy_path[i+1]) for i in range(len(greedy_path)-1)]
            nx.draw_networkx_edges(G, node_positions, edgelist=greedy_edges, 
                                   width=3, edge_color='green', alpha=0.6)
        
        # Gambar jalur A* jika ada
        if astar_path and len(astar_path) > 1:
            astar_edges = [(astar_path[i], astar_path[i+1]) for i in range(len(astar_path)-1)]
            nx.draw_networkx_edges(G, node_positions, edgelist=astar_edges, 
                                   width=3, edge_color='red', alpha=0.6)
        
        # Legend
        if greedy_path or astar_path:
            legend_elements = []
            if greedy_path:
                legend_elements.append(plt.Line2D([0], [0], color='green', lw=3, alpha=0.6, label='Greedy Path'))
            if astar_path:
                legend_elements.append(plt.Line2D([0], [0], color='red', lw=3, alpha=0.6, label='A* Path'))
            ax.legend(handles=legend_elements, loc='upper right')
        
        ax.set_title("Graf dengan Bobot dan Nilai Heuristik")
        plt.axis('off')
        
        # Tampilkan dalam Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def search_routes(self):
        start = self.start_var.get()
        goal = self.goal_var.get()
        
        if not start or not goal:
            messagebox.showerror("Error", "Harap pilih node asal dan tujuan!")
            return
        
        # Hitung nilai heuristik berdasarkan jarak ke node tujuan
        self.heuristic = calculate_heuristic(graph, goal)
        
        # Tampilkan informasi heuristik
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "--- Nilai Heuristik ---\n")
        for node in sorted(self.heuristic.keys()):
            self.result_text.insert(tk.END, f"h({node}) = {self.heuristic[node]}\n")
        self.result_text.insert(tk.END, "\n")
        
        # Jalankan algoritma pencarian
        greedy_path, greedy_cost = greedy_best_first_search(graph, start, goal, self.heuristic)
        astar_path, astar_cost = a_star_search(graph, start, goal, self.heuristic)
        
        # Tampilkan hasil Greedy
        self.result_text.insert(tk.END, "--- Greedy Best First Search ---\n")
        if greedy_path:
            self.result_text.insert(tk.END, f"Jalur: {' -> '.join(greedy_path)}\n")
            self.result_text.insert(tk.END, f"Total cost: {greedy_cost}\n\n")
        else:
            self.result_text.insert(tk.END, f"Tidak ada jalur dari {start} ke {goal}\n\n")
        
        # Tampilkan hasil A*
        self.result_text.insert(tk.END, "--- A* Search ---\n")
        if astar_path:
            self.result_text.insert(tk.END, f"Jalur: {' -> '.join(astar_path)}\n")
            self.result_text.insert(tk.END, f"Total cost: {astar_cost}\n")
        else:
            self.result_text.insert(tk.END, f"Tidak ada jalur dari {start} ke {goal}\n")
        
        # Gambar graf dengan jalur
        self.draw_graph(greedy_path, astar_path)

# Program utama
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = HeuristicSearchApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Terjadi kesalahan: {e}")