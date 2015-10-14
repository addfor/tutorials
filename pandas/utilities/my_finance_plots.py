import numpy as np
from pylab import *
from pandas import *
#from pandas.io.data import *
    
def montecarloPlot(S):
    cols, rows = S.shape
    a = arange(0,cols)
    x = append(a,a[::-1])
    
    figure(figsize=(10, 8), dpi=80)
    gs = plt.GridSpec(4, 4)
    ax1 = plt.subplot(gs[:, 0:3])
    
    cmap = cm.jet
    for i in [0, 1, 5]:
        lower_bound = np.percentile(S, i, axis=1)
        upper_bound = np.percentile(S, 100-i, axis=1)
        y= append(lower_bound,upper_bound[::-1])
        fill(x,y,'r',facecolor=cmap(i*255/50), alpha=0.3+i/100.)
    
    ax2 = plt.subplot(gs[:, 3])
    
    hist( S.ravel(), bins= 101, orientation='horizontal'  )
    ax2.xaxis.set_major_locator(MaxNLocator(4))
    xlabels = ax2.get_xticklabels() 
    for label in xlabels: 
        label.set_rotation(45) 
    
    setp(ax2.get_xticklabels(), visible=False)
    setp(ax2.get_yticklabels(), visible=False); grid(True); show()
