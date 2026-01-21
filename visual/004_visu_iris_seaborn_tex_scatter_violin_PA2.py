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

# --- NOWY WYKRES: VIOLIN PLOT DLA PORÓWNANIA ROZKŁADÓW ---

# Utworzenie nowej figury
fig_violin, ax_violin = plt.subplots(figsize=(8, 6))

# Generowanie wykresu skrzypcowego
sns.violinplot(
    x='species', 
    y='sepal_length', 
    data=iris, 
    ax=ax_violin, 
    palette="pastel", # Użycie delikatniejszej palety kolorów
    inner="quartile"  # Pokazanie kwartyli (Q1, Q2/mediana, Q3) wewnątrz skrzypiec
)

# Łączenie formuły LaTeX w tytule
ax_violin.set_title(
    r"Porównanie Rozkładów Długości Działki Kielicha" 
    r"\newline Mediana (Kwantyl $Q_2$): $Q_2(\mathbf{X}) = \text{argmin}_m \sum_{i} |x_i - m|$", 
    fontsize=14
)

# Etykiety osi
ax_violin.set_xlabel(r"Gatunek Iris ($\mathbf{C}$)", fontsize=12)
ax_violin.set_ylabel(r"Długość Działki Kielicha ($\mathbf{L}_s$)", fontsize=12)

plt.savefig("violin_iris_tex.png")
plt.show()


