# Sigmoid function in Python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-5, 5, 50)
z = 1/(1 + np.exp(-x))

plt.subplots(figsize=(8, 5))
plt.plot(x, z)
plt.grid()
plt.show()


