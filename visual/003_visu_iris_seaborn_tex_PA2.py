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

# Problem 1: sns.pairplot generuje własną siatkę figur (nie używa fig/ax)
# Zmieniamy to na plt.figure() aby mieć kontrolę nad oknem.
plt.figure(figsize=(10, 8)) 

sns.pairplot(iris, hue="species", markers=["o", "s", "D"])

# plt.suptitle odnosi się do całego okna figure, to jest poprawne miejsce na główny tytuł
plt.suptitle(r"Wpływ Regularyzacji na Krzywą Uczenia w $\mathbf{Modelu}$", fontsize=16, y=1.02)
# Używamy plt.title/ax.set_title/plt.suptitle tylko raz

# Zapis wykresu do pliku
plt.savefig("pairplot_iris_tex.png") 

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


