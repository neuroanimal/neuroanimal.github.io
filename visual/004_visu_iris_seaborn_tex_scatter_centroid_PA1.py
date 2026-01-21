import seaborn as sns
import matplotlib.pyplot as plt

# --- KONFIGURACJA LATEX ---
latex_packages = [
    r'\usepackage[T1]{fontenc}', r'\usepackage[utf8]{inputenc}', 
    r'\usepackage{amsmath}', r'\usepackage{lmodern}', 
    r'\usepackage[polish]{babel}', r'\usepackage{graphicx}'
]

plt.rcParams.update({
    "text.usetex": True,
    "mathtext.fontset": "cm",
    "text.latex.preamble": '\n'.join(latex_packages)
})

# Wczytanie danych
iris = sns.load_dataset("iris")

# --- NOWY WYKRES: SCATTER PLOT Z CENTROIDAMI ---

# Utworzenie nowej figury
fig_cent, ax_cent = plt.subplots(figsize=(8, 6))

# Obliczenie centroidów (średniej) dla każdej cechy
centroids = iris.groupby('species')[['petal_length', 'petal_width']].mean()

# Rysowanie punktów danych
sns.scatterplot(
    x='petal_length', 
    y='petal_width', 
    hue='species', 
    data=iris, 
    ax=ax_cent,
    s=70, # Rozmiar punktów
    alpha=0.7
)

# Rysowanie centroidów (środków ciężkości)
ax_cent.scatter(
    centroids['petal_length'], 
    centroids['petal_width'], 
    marker='X', # Użycie markera X
    s=200,      # Duży rozmiar
    color='k',  # Kolor czarny
    label='Centroid'
)

# łączenie formuły LaTeX w tytule z obliczeniami
ax_cent.set_title(
    r"Separowalność Klas: Długość vs Szerokość Płatka" 
    r"\newline Centroid (Środek Ciężkości Klasy $\mathbf{k}$): " 
    r"$\boldsymbol{\mu}_k = \frac{1}{N_k}\sum_{i \in \mathcal{C}_k} \mathbf{x}_i$", 
    fontsize=14
)
# Uwaga: \newline wymaga dodania \usepackage{amsmath} i działa w trybie suptitle/title

ax_cent.set_xlabel(r"Długość Płatka ($\mathbf{L}_p$)", fontsize=12)
ax_cent.set_ylabel(r"Szerokość Płatka ($\mathbf{W}_p$)", fontsize=12)
ax_cent.legend(title=r"Gatunek ($\mathbf{C}$)")
ax_cent.grid(True, linestyle='--', alpha=0.6)

plt.savefig("centroid_iris_tex.png")
plt.show()



