import numpy as np
import bokeh.plotting as bk

def test_func(x, err=0.5):
    return np.random.normal(10 - 1. / (x + 0.1), err)

def compute_error(x, y, p):
    yfit = np.polyval(p, x)
    return np.sqrt(np.mean((y - yfit) ** 2))

def plot_bias_variance(N=8, random_seed=42, err=0.5):
    np.random.seed(random_seed)
    x = 10 ** np.linspace(-2, 0, N)
    y = test_func(x)
    xfit = np.linspace(-0.2, 1.2, 1000)
    titles = ['d = 1 (under-fit; high bias)',
              'd = 2',
              'd = 6 (over-fit; high variance)']
    degrees = [1, 2, 6]
    
    row = []
    for i, d in enumerate(degrees):
        fig = bk.figure(plot_width=240, plot_height=240,
                        title=titles[i], x_range=(-0.2, 1.2), y_range=(0, 12))
        fig.title.text_font_size = '11pt'
        fig.xaxis.axis_label_text_font_size = '9pt'
        fig.yaxis.axis_label_text_font_size = '9pt'
        fig.x(x, y, color='black', size=12)
        
        p = np.polyfit(x, y, d)
        yfit = np.polyval(p, xfit)
        fig.line(xfit, yfit, line_color='blue')
        
        fig.xaxis.axis_label = 'house size'
        fig.xaxis.axis_label_text_font_size = '9pt'
        if i == 0:
            fig.yaxis.axis_label = 'price'
        row.append(fig)

    gp = bk.gridplot([row], border_space=0)
    bk.show(gp)

