"""NetworkX graphs do not have events that can be listened to.  In order to 
watch the NetworkX graph object for changes a custom eventful graph object must 
be created.  The custom eventful graph object will inherit from the base graph 
object and use special eventful dictionaries instead of standard Python dict 
instances.  Because NetworkX nests dictionaries inside dictionaries, it's 
important that the eventful dictionary is capable of recognizing when a 
dictionary value is set to another dictionary instance.  When this happens, the 
eventful dictionary needs to also make the new dictionary an eventful 
dictionary.  This allows the eventful dictionary to listen to changes made to 
dictionaries within dictionaries."""
import networkx
from networkx.generators.classic import empty_graph

from eventful_dict import EventfulDict

class EventfulGraph(networkx.Graph):

    _constructed_callback = None

    @staticmethod
    def on_constructed(callback):
        """Register a callback to be called when a graph is constructed."""
        if callback is None or callable(callback):
            EventfulGraph._constructed_callback = callback
    
    def __init__(self, *pargs, **kwargs):
        """Initialize a graph with edges, name, graph attributes.
        
        Parameters
        sleep: float
            optional float that allows you to tell the
        dictionary to hang for the given amount of seconds on each
        event.  This is usefull for animations."""
        super(EventfulGraph, self).__init__(*pargs, **kwargs)

        # Override internal dictionaries with custom eventful ones.
        sleep = kwargs.get('sleep', 0.0)
        self.graph = EventfulDict(self.graph, sleep=sleep)
        self.node = EventfulDict(self.node, sleep=sleep)
        self.adj = EventfulDict(self.adj, sleep=sleep)

        # Notify callback of construction event.
        if EventfulGraph._constructed_callback:
            EventfulGraph._constructed_callback(self)


def empty_eventfulgraph_hook(*pargs, **kwargs):
    def wrapped(*wpargs, **wkwargs):
        """Wrapper for networkx.generators.classic.empty_graph(...)"""
        wkwargs['create_using'] = EventfulGraph(*pargs, **kwargs)
        return empty_graph(*wpargs, **wkwargs)
    return wrapped
