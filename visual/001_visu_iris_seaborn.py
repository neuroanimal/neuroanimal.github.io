import seaborn as sns
import matplotlib.pyplot as plt

# Wczytanie wbudowanego zestawu danych Iris
iris = sns.load_dataset("iris")

# Utworzenie Wykresu Par
# Wizualizacja relacji między wszystkimi parami cech,
# z rozkładami na przekątnej i zróżnicowaniem kolorystycznym wg. gatunku (species).
sns.pairplot(iris, hue="species", markers=["o", "s", "D"])
plt.suptitle("Wykres Par (Pair Plot) dla zbioru Iris - Analiza EDA", y=1.02)

# Zapis wykresu do pliku (do włączenia w dokumencie LaTeX)
plt.savefig("pairplot_iris.png")
plt.show()


