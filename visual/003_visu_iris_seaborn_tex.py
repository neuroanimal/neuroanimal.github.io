import seaborn as sns
import matplotlib.pyplot as plt

# Ustawienie, które włącza renderowanie LaTeX w tekście Matplotlib
## plt.rcParams['text.usetex'] = True
# 1. Konfiguracja Matplotlib dla LaTeX
# - Włączenie renderowania LaTeX
# - Czcionka do matematyki (poprawia wygląd i rozwiązuje niektóre konflikty)
# 2. DODANIE WYMAGANEJ PREAMBUŁY DLA JĘZYKA POLSKIEGO
plt.rcParams.update({
    "text.usetex": True,
    "mathtext.fontset": "cm", 
    "text.latex.preamble": [
        r'\usepackage[T1]{fontenc}',
        r'\usepackage[utf8]{inputenc}',
        r'\usepackage{amsmath}',      # Dla symboli matematycznych
        r'\usepackage{lmodern}',     # Dla lepszych czcionek, rozwiązuje błędy z type1ec.sty
        r'\usepackage[polish]{babel}', # Dla obsługi polskich znaków
        r'\usepackage{graphicx}'
    ]
})

# Wczytanie wbudowanego zestawu danych Iris
iris = sns.load_dataset("iris")

fig, ax = plt.subplots()
ax.set_title(r"Funkcja Gęstości $f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}$")

# Utworzenie Wykresu Par
# Wizualizacja relacji między wszystkimi parami cech,
# z rozkładami na przekątnej i zróżnicowaniem kolorystycznym wg. gatunku (species).
sns.pairplot(iris, hue="species", markers=["o", "s", "D"])
plt.suptitle("Wykres Par (Pair Plot) dla zbioru Iris - Analiza EDA", y=1.02)

# Przykład użycia polskiej diakrytyki w tytule
plt.title(r"Wpływ Regularyzacji na Krzywą Uczenia w $\mathbf{Modelu}$", fontsize=16)

# Zapis wykresu do pliku (do włączenia w dokumencie LaTeX)
plt.savefig("pairplot_iris.png")
plt.show()


