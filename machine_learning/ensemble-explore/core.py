import numpy as np
import random
import enum
from collections import defaultdict
from pprint import pprint

from sklearn.ensemble import BaseEnsemble
from sklearn.tree.tree import BaseDecisionTree
from sklearn.base import ClassifierMixin

## TODO Remove
def distribution(samples, nbins=10, range_=None):
    if len(samples) == 0:
        return []
    
    bins = [ 0 ] * nbins
    if range_ is None:
        range_ = (min(samples), max(samples))
        
    a, b = range_
    if a == b:
        return [ (len(samples), a) ]
    
    bin_size = float(b-a) / nbins
    for sample in samples:
        sample = max(0, sample - a)
        sample = min(b-a, sample)
        # now sample is in [0, b-a]
        bin_id = int(sample / bin_size)
        if bin_id == len(bins):
            bin_id -= 1
        bins[bin_id] += 1

    counts = []
    limits = []
    for i, count in enumerate(bins):
        counts.append(count)
        limits.append(a + i*bin_size)
    limits.append(b)

    return {
        'bins': counts,
        'limits': limits,
        'range': (a, b)
    }


## TODO Remove
def random_subtree(max_features=6, max_depth=3, node_id=0):
    children = {}
    children_ids = []

    if max_depth > 1:
        # n_children = random.randint(int(max_features/2),max_features)
        for i in range(max_features):
            child_id = max_features*(node_id+1) + i + 1
            children_ids.append(child_id)
            children.update(random_subtree(max_features=max_features,
                                           max_depth=max_depth-1,
                                           node_id=child_id))
        
    thresholds = [ random.normalvariate(5, 2)
                   for i in range(max_features**max_depth) ]
    nodes = {
        node_id: {
            'feature': random.randint(0, max_features-1),
            'threshold': distribution(thresholds),
            'children': children_ids,
            'level': max_depth
        }
    }
    
    nodes.update(children)
    return nodes

class EnsembleType(enum.Enum):
    regressor = 1
    classifier = 2
    
class AggregateTreeBuilder:
    """An aggregate tree, represented as a nested dictionary.
This form is more suitable for building the aggregate tree
starting from a collection of trees from an ensemble."""
    
    def __init__(self, ensemble_type):
        if not isinstance(ensemble_type, EnsembleType):
            ensemble_type = EnsembleType[ensemble_type]
        
        self.root = self.new_node()
        self.ensemble_type = ensemble_type
        
    def new_node(self):
        T = {
            'count': 0,
            'num_samples': [],
            'threshold': [],
            'children': defaultdict(lambda: self.new_node()),
        }
        return T

    def add_decision_tree(self, tree, node_id=0, T=None):
        """Adds a scikit-learn decision tree to the aggregate currently being built.
The tree is supposed to be one of DecisionTreeRegressor, DecisionTreeClassifier, Tree."""
        if T is None:
            T = self.root
            
        if isinstance(tree, BaseDecisionTree):
            tree = tree.tree_
            
        # identifiers SHOULD be strings
        feature = str(tree.feature[node_id])
        child = T['children'][feature]
        
        child['featureId'] = feature
        child['count'] += 1
        child['threshold'].append(tree.threshold[node_id])
        child['num_samples'].append(tree.n_node_samples[node_id])
        if tree.children_left[node_id] == -1: # if node is leaf...
            value_matrix = tree.value[node_id]
            n_outputs = tree.n_outputs
            max_n_classes = tree.max_n_classes
            # value_matrix is: output -> class -> value
            child['max_n_classes'] = max_n_classes
            if 'value' not in child:
                child['value'] = defaultdict(list)
            if self.ensemble_type == EnsembleType.regressor:
                for output_id in range(n_outputs):
                    child['value'][output_id].append(value_matrix[output_id][0])
            else:
                for output_id in range(n_outputs):
                    for class_id in range(max_n_classes):
                        n_samples = int(value_matrix[output_id][class_id])
                        for i in range(n_samples):
                            child['value'][output_id].append(class_id)

        left_id = tree.children_left[node_id]
        if left_id != -1:
            self.add_decision_tree(tree, node_id=left_id, T=child)

        right_id = tree.children_right[node_id]
        if right_id != -1:
            self.add_decision_tree(tree, node_id=right_id, T=child)

    def recompute_dists(self, nbins=15):
        pass
    
    # def collect_outputs(self):
    #     if node is None:
    #         node = self.root
            
    #     if len(node['children']) == 0:
    #         return

    #     children = node['children']
    #     for child in children.itervalues():
    #         self.collect_outputs_reg(child)

    #     first_child = children[ children.iterkeys().next() ]
    #     max_n_classes = len(first_child['value'][0])
    #     node['value'] = defaultdict(list)
    #     for child in node['children'].itervalues():
    #         for output_id, values in child['value'].iteritems():
    #             node['value'][output_id].append(values)

    def reassign_ids(self):
        # (re)assign ids
        queue = [self.root]
        last_id = 0
        while len(queue) > 0:
            node = queue.pop(0)
            node['id'] = str(last_id)
            last_id += 1
            queue.extend(node['children'].itervalues())

    def flatten(self):
        """Converts this tree from the nested dict form to an array of flat
dicts, where each node is identified by a unique numeric id. Each
reference to a node is substituted with the referred node's id. """

        self.reassign_ids()
        
        by_id = {}
        queue = [self.root]
        while len(queue) > 0:
            node = queue.pop(0)
            id = node['id']
            
            new_node = dict(node)
            # if 'value' in new_node:
            #     # numpy arrays should be converted to list
            #     new_node['value'] = { k: v.tolist() for k, v in new_node['value'].iteritems() }
            new_node['children'] = [ n['id'] for n in new_node['children'].itervalues() ]
            by_id[id] = new_node
            
            queue.extend(node['children'].itervalues())
        return by_id
                    
class AggregateTree(object):
    """An aggregate tree built from the given scikit-learn ensemble or
collection of decision trees (parameter `estimator_or_trees').  In the
latter case, decision trees are supposed to be instances of
scikit-learn's DecisionTreeClassifier, DecisionTreeRegressor, or Tree.

This form is more suitable for querying parts of the tree, with
relationships represented by primary and foreign keys (as in the
relational model, common in databases.)"""
    
    def __init__(self, estimator_or_trees, ensemble_type=None):
        if isinstance(estimator_or_trees, BaseEnsemble):
            ensemble = estimator_or_trees
            trees = [ e.tree_ for e in ensemble.estimators_ ]
            if ensemble_type is None:
                if isinstance(ensemble, ClassifierMixin):
                    ensemble_type = EnsembleType.classifier
                else:
                    ensemble_type = EnsembleType.regressor
        else:
            if ensemble_type is None:
                raise ValueError("ensemble_type must be given when "
                                 "estimator_or_trees is a list of decision trees")

            if isinstance(estimator_or_trees, BaseDecisionTree):
                trees = [ estimator.tree_ ]
            else:
                trees = estimator_or_trees

        builder = AggregateTreeBuilder(ensemble_type)

        for tree in trees:
            builder.add_decision_tree(tree)

        builder.recompute_dists()
        # builder.collect_outputs()
        self.by_id = builder.flatten()
        
    def get(self, id='root'):
        if id == 'root':
            id = 0
        return self.by_id[str(id)]

    def breadth_search(self, node_id='root', max_depth=None):
        root = self.get(node_id)

        queue = [(root, 0)]
        while len(queue) > 0:
            node, depth = queue.pop(0)
            if max_depth is not None and depth > max_depth:
                break
            
            yield node, depth

            for child_id in node['children']:
                queue.append((self.get(child_id), depth+1))

    def query(self, start_id='root', max_depth=None):
        ret = {}
        gen = self.breadth_search(start_id, max_depth=max_depth)
        for node, depth in gen:
            ret[node['id']] = node
        return ret


