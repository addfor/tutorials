import numpy as np
import matplotlib.pyplot as plt

def plot_01():
    image = np.random.randn(120, 120)
    plt.imshow(image, cmap=plt.cm.hot)    
    plt.colorbar()
    plt.show()

if __name__ == '__main__':
    plot_01()
    plt.show()