# %%

import numpy as np
import matplotlib.pyplot as plt

y = np.array([10, 20, 30, 40, 50, 60])
x = np.arange(len(y))
# f, (ax1, ax2) = plt.subplots(2, sharex=True)
# ax1.scatter(x, y, s=0.5)
# ax1.plot(y)

# print(np.gradient(y))
# g = np.rad2deg(np.arctan(y))
# print(g)
grad = np.arctan(y)
print(grad)
# ax2.plot(grad)


# plt.show()
