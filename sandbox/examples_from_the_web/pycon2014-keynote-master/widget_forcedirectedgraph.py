from IPython.html import widgets # Widget definitions
from IPython.utils.traitlets import Unicode, CInt, CFloat # Import the base Widget class and the traitlets Unicode class.
from IPython.display import display, Javascript

def publish_js():
    with open('./widget_forcedirectedgraph.js', 'r') as f:
        display(Javascript(data=f.read()))


# Define our ForceDirectedGraphWidget and its target model and default view.
class ForceDirectedGraphWidget(widgets.DOMWidget):
    _view_name = Unicode('D3ForceDirectedGraphView', sync=True)
    
    width = CInt(400, sync=True)
    height = CInt(300, sync=True)
    charge = CFloat(270., sync=True)
    distance = CInt(30., sync=True)
    strength = CInt(0.3, sync=True)
    
    def __init__(self, eventful_graph, *pargs, **kwargs):
        widgets.DOMWidget.__init__(self, *pargs, **kwargs)
        
        self._eventful_graph = eventful_graph
        self._send_dict_changes(eventful_graph.graph, 'graph')
        self._send_dict_changes(eventful_graph.node, 'node')
        self._send_dict_changes(eventful_graph.adj, 'adj')

    def _ipython_display_(self, *pargs, **kwargs):
        
        # Show the widget, then send the current state
        widgets.DOMWidget._ipython_display_(self, *pargs, **kwargs)
        for (key, value) in self._eventful_graph.graph.items():
            self.send({'dict': 'graph', 'action': 'add', 'key': key, 'value': value})
        for (key, value) in self._eventful_graph.node.items():
            self.send({'dict': 'node', 'action': 'add', 'key': key, 'value': value})
        for (key, value) in self._eventful_graph.adj.items():
            self.send({'dict': 'adj', 'action': 'add', 'key': key, 'value': value})

    def _send_dict_changes(self, eventful_dict, dict_name):
        def key_add(key, value):
            self.send({'dict': dict_name, 'action': 'add', 'key': key, 'value': value})
        def key_set(key, value):
            self.send({'dict': dict_name, 'action': 'set', 'key': key, 'value': value})
        def key_del(key):
            self.send({'dict': dict_name, 'action': 'del', 'key': key})
        eventful_dict.on_add(key_add)
        eventful_dict.on_set(key_set)
        eventful_dict.on_del(key_del)
