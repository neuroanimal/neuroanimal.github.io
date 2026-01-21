import seaborn as sns
import matplotlib.pyplot as plt

# --- KONFIGURACJA LATEX (pozostaje bez zmian) ---
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
fig_pair_grid = sns.pairplot(iris, hue="species", markers=["o", "s", "D"])
fig = fig_pair_grid.fig # Pobieramy obiekt Figure

# Usunięcie 'fig.subplots_adjust(top=0.90)' – nie pomogło.

# NOWA, AGRESYWNA METODA: Użycie set_title na pierwszej osi i przesunięcie
fig_pair_grid.axes[0, 0].set_title(
    r"Wpływ Regularyzacji na Krzywą Uczenia w $\mathbf{Modelu}$",
    fontsize=16, 
    loc='center', # Ustawienie wyśrodkowania na osi
    pad=20        # Dodanie odstępu, aby tytuł był widoczny
)

fig.savefig("pairplot_iris_tex.png")

# --- WYKRES 2: HISTOGRAM (pozostaje bez zmian) ---
fig_hist, ax_hist = plt.subplots(figsize=(8, 6))
ax_hist.hist(iris['sepal_length'], bins=20, color='lightblue', edgecolor='black')

ax_hist.set_title(r"Rozkład Długości Działki Kielicha $\mathbf{w\ oparciu\ o}\ \sigma\sqrt{2\pi}$", 
                  fontsize=14) 
ax_hist.set_xlabel(r"Długość [$\mathbf{cm}$]", fontsize=12)

plt.savefig("hist_iris_tex.png")

plt.show()


