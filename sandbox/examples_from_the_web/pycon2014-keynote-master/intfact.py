from IPython.html import widgets
from IPython.display import display
from eventful_graph import EventfulGraph
from widget_forcedirectedgraph import ForceDirectedGraphWidget, publish_js
publish_js()


BACKGROUND = '#FFFFFF'
PARENT_COLOR = '#3E5970'
FACTOR_COLOR = '#424357'
EDGE_COLOR = '#000000'
PRIME_COLOR = '#FF5555'

existing_graphs = []

def handle_graph(graph):
    if len(existing_graphs) > 0:
        for graph_popup in existing_graphs:
            graph_popup.close()
        del existing_graphs[:]
        
    floating_container = widgets.ContainerWidget()
    floating_container.description = "Factors"
    floating_container.button_text = "Factors"
    floating_container.set_css({
        'width': '620px',
        'height': '450px'}, selector='modal')
        
    d3 = ForceDirectedGraphWidget(graph)
    d3.charge = -400.
    floating_container.children = [d3]
    floating_container.set_css('background', BACKGROUND)
    d3.width = 600
    d3.height = 400
    display(floating_container)
    existing_graphs.append(floating_container)
EventfulGraph.on_constructed(handle_graph)

###

CHARGE = -200
MIN_NODE_RADIUS = 15.0
START_NODE_RADIUS = 65.0
is_int = lambda x: int(x) == x
factor = lambda x: [i + 1 for i in range(x-1) if  i != 0 and is_int(x / (float(i) + 1.0))]
calc_node_size = lambda x, start_x: max(float(x)/start_x * START_NODE_RADIUS, MIN_NODE_RADIUS)
calc_edge_length = lambda x, parent_x, start_x: calc_node_size(x, start_x) + calc_node_size(parent_x, start_x)
    
def add_node(graph, value, **kwargs):
    graph.add_node(len(graph.node), charge=CHARGE, strokewidth=0, value=value, label=value, font_size='18pt', dy='8', **kwargs)
    return len(graph.node) - 1
    
def add_child_node(graph, x, number, start_number, parent):
    index = add_node(graph, x, fill=FACTOR_COLOR, r='%.2fpx' % calc_node_size(x, start_number))
    graph.add_edge(index, parent, distance=calc_edge_length(x, number, start_number), stroke=EDGE_COLOR, strokewidth='3px')
    return index

def plot_primes(number, start_number=None, parent=None, graph=None, delay=0.0):
    start_number = start_number or number
    graph = graph or EventfulGraph(sleep=delay)
    parent = parent or add_node(graph, number, fill=PARENT_COLOR, r='%.2fpx' % START_NODE_RADIUS)
    
    factors = factor(number)
    if len(factors) == 0:
        graph.node[parent]['fill'] = PRIME_COLOR
    for x in factors:
        index = add_child_node(graph, x, number, start_number, parent)
        plot_primes(x, start_number, parent=index, graph=graph)


####
def factorizer():
    box = widgets.ContainerWidget()
    header = widgets.HTMLWidget(value="<h1>Integer Factorizer</h1><br>")
    number = widgets.IntSliderWidget(description="Number:", value=100)
    speed = widgets.FloatSliderWidget(description="Delay:", min=0.0, max=0.2, value=0.1, step=0.01)

    subbox = widgets.ContainerWidget()
    button = widgets.ButtonWidget(description="Calculate")
    subbox.children = [button]

    box.children = [header, number, speed, subbox]
    display(box)

    box.add_class('align-center')
    box.add_class('center')
    box.add_class('well well-small')
    box.set_css('width', 'auto')

    subbox.remove_class('vbox')
    subbox.add_class('hbox')
    # subbox.add_class('end')

    def handle_caclulate(sender):
        plot_primes(number.value, delay=speed.value)
    button.on_click(handle_caclulate)
