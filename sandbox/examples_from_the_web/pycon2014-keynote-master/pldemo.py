import numpy as np

nr = np.random
distributions = [nr.uniform, nr.normal , 
                 lambda size: nr.beta(a=0.5, b=2, size=size)]

names = ['Uniform(0,1)', 'Normal(0,1)', 'beta(a=0.5, b=2)']

boxes = [{'y': dist(size=50), 'type': 'box', 'boxpoints': 'all', 'jitter': 0.5, 'pointpos': -1.8,
        'name': name} for dist, name in zip(distributions, names)]

layout = {'title': 'A few distributions',
          'showlegend': False,
          'xaxis': {'ticks': '', 'showgrid': False, 'showline': False},
          'yaxis': {'zeroline': False, 'ticks': '', 'showline': False},
          }
