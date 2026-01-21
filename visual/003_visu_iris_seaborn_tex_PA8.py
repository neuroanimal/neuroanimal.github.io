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

# --- WYKRES 1: PAIR PLOT ---
fig_pair_grid = sns.pairplot(iris, hue="species", markers=["o", "s", "D"])
fig = fig_pair_grid.fig # Pobieramy obiekt Figure

# 1. KLUCZOWA POPRAWKA: RĘCZNE ZWALNIANIE MIEJSCA DLA TYTUŁU
fig.subplots_adjust(top=0.92) 

# 2. POPRAWKA A: DODANIE ZNAKÓW DOLARA DLA RENDERINGU \mathbf{Modelu}
fig.suptitle(r"Wpływ Regularyzacji na Krzywą Uczenia w $\mathbf{Modelu}$", 
             fontsize=16, y=0.98) 

fig.savefig("pairplot_iris_tex.png")


# --- WYKRES 2: HISTOGRAM ---
fig_hist, ax_hist = plt.subplots(figsize=(8, 6))
ax_hist.hist(iris['sepal_length'], bins=20, color='lightblue', edgecolor='black')

# POPRAWKA B: POGRUBIENIE CAŁEJ FORMUŁY
ax_hist.set_title(r"Rozkład Długości Działki Kielicha $\mathbf{w\ oparciu\ o\ \mathbf{\sigma\sqrt{2\pi}}}$", 
                  fontsize=14) 
ax_hist.set_xlabel(r"Długość [$\mathbf{cm}$]", fontsize=12)

plt.savefig("hist_iris_tex.png")

plt.show()


