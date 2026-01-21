import seaborn as sns
import matplotlib.pyplot as plt

# --- KONFIGURACJA LATEX ---
latex_packages = [
    r'\usepackage[T1]{fontenc}',
    r'\usepackage[utf8]{inputenc}',
    r'\usepackage{amsmath}',      
    r'\usepackage{lmodern}',      
    r'\usepackage[polish]{babel}', 
    r'\usepackage{graphicx}'
]

plt.rcParams.update({
    "text.usetex": True,
    "mathtext.fontset": "cm",
    "text.latex.preamble": '\n'.join(latex_packages)
})

# Wczytanie danych
iris = sns.load_dataset("iris")

# --- WYKRES 1: PAIR PLOT ---
# Generowanie PairGrid
fig_pair_grid = sns.pairplot(iris, hue="species", markers=["o", "s", "D"])

# POPRAWKA B: UŻYWAMY fig.suptitle NA OBIEKCIE FIGURE
# Gwarantuje to, że Matplotlib użyje konfiguracji LaTeX
fig_pair_grid.fig.suptitle(r"Wpływ Regularyzacji na Krzywą Uczenia w $\mathbf{Modelu}$", 
                           fontsize=16, y=1.02)

fig_pair_grid.fig.savefig("pairplot_iris_tex.png")


# --- WYKRES 2: HISTOGRAM ---
fig_hist, ax_hist = plt.subplots(figsize=(8, 6))
ax_hist.hist(iris['sepal_length'], bins=20, color='lightblue', edgecolor='black')

# POPRAWKA A: WZÓR UJĘTY W DOLARY ($$) I POPRAWIONA FORMUŁA
ax_hist.set_title(r"Rozkład Długości Działki Kielicha $\mathbf{w\ oparciu\ o}\ \sigma\sqrt{2\pi}$", 
                  fontsize=14) 
ax_hist.set_xlabel(r"Długość [$\mathbf{cm}$]", fontsize=12)

plt.savefig("hist_iris_tex.png")

plt.show()


