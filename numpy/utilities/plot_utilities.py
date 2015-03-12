import numpy as np
import bokeh.plotting as bk

def plot_01():
    image = np.random.randn(120, 120)
    fig = bk.figure()
    fig.image([image], x=[0], y=[0], dw=[1], dh=[1], palette='OrRd9')
    return fig

if __name__ == '__main__':
    fig = plot_01()
    bk.show(fig)
