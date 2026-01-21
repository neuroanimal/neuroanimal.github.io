import seaborn as sns
import matplotlib.pyplot as plt

# 1. Konfiguracja Matplotlib dla LaTeX (PREAMBUŁA JAKO POJEDYNCZY STRING)
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
    # Połączenie listy pakietów w jeden string oddzielony znakiem nowej linii
    "text.latex.preamble": '\n'.join(latex_packages)
})

# Wczytanie wbudowanego zestawu danych Iris
iris = sns.load_dataset("iris")

# --- GENEROWANIE WYKRESÓW ---

# 1. GENEROWANIE WYKRESU PAIR PLOT
# sns.pairplot zwraca obiekt Figure. Przechwytujemy go jako 'fig_pair'
fig_pair = sns.pairplot(iris, hue="species", markers=["o", "s", "D"])

# 2. DODANIE TYTUŁU DO PRZECHWYCONEJ FIGURY
# Używamy fig_pair.suptitle zamiast plt.suptitle
fig_pair.fig.suptitle(r"Wpływ Regularyzacji na Krzywą Uczenia w $\mathbf{Modelu}$", fontsize=16, y=1.02)

# Zapis wykresu (fig_pair ma wbudowaną funkcję savefig)
fig_pair.fig.savefig("pairplot_iris_tex.png")

# --- PRZYKŁAD KORZYSTANIA Z FIG, AX I SET_TITLE (POPRAWNY SPOSÓB) ---

# Ten fragment jest tylko demonstracją jak to zrobić poprawnie z fig/ax
# Wyrzuć go, jeśli nie chcesz drugiego wykresu
fig_hist, ax_hist = plt.subplots(figsize=(8, 6))
ax_hist.hist(iris['sepal_length'], bins=20, color='lightblue', edgecolor='black')
# Poprawne użycie LaTeX-u w tytule AXES (OŚ)
ax_hist.set_title(r"Rozkład Długości Działki Kielicha $\sigma\sqrt{2\pi}$", fontsize=14) 
ax_hist.set_xlabel(r"Długość [$\mathbf{cm}$]", fontsize=12)
plt.savefig("hist_iris_tex.png")


plt.show()


