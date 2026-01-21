# ReLU in Python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-5, 5, 50)
z = [max(0, i) for i in x]

plt.subplots(figsize=(8, 5))
plt.plot(x, z)
plt.grid()
plt.show()


