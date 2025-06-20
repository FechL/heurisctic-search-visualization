# Data training
data = [
    (9, 2000000, 3, "sedang"),
    (10, 2500000, 2, "sedang"),
    (15, 4000000, 2, "sedang"),
    (30, 5000000, 4, "kaya"),
    (16, 5350000, 3, "kaya"),
    (25, 7000000, 5, "kaya"),
    (9, 500000, 0.5, "miskin"),
    (8, 700000, 1, "miskin"),
    (10, 1500000, 2, "miskin"),
    (14, 1000000, 1, "miskin")
]

# Data uji
test_data = (12, 1750000, 2)

# Normalisasi menggunakan Min-Max Scaling
min_values = [min([row[i] for row in data]) for i in range(3)]
max_values = [max([row[i] for row in data]) for i in range(3)]

def normalize(value, min_val, max_val):
    return (value - min_val) / (max_val - min_val)

normalized_data = [
    ([normalize(row[i], min_values[i], max_values[i]) for i in range(3)], row[3])
    for row in data
]
norm_test_data = [normalize(test_data[i], min_values[i], max_values[i]) for i in range(3)]

# Fungsi jarak euclidean
def euclidean_distance(p1, p2):
    return sum((p1[i] - p2[i]) ** 2 for i in range(len(p1))) ** 0.5

# Hitung jarak ke semua data
jarak = [(euclidean_distance(norm_test_data, row[0]), row[1]) for row in normalized_data]

# Urutkan  jarak terdekat
jarak.sort()

# Ambil 3 tetangga terdekat
k = 3
nearest_neighbors = jarak[:k]

# Tentukan kategori mayoritas
from collections import Counter
kategori_terdekat = [neighbor[1] for neighbor in nearest_neighbors]
kategori_terpilih = Counter(kategori_terdekat).most_common(1)[0][0]

# Output hasil
print("Kategori prediksi untuk data uji:", kategori_terpilih)
