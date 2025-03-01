import matplotlib.pyplot as plt
import numpy as np


data = np.random.random(1000000)

plt.hist(data, bins=10)
plt.show()