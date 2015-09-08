from flask import Flask, render_template, send_from_directory 
from flask import request
from Queue import Empty as QueueEmpty
from multiprocessing import queues
from multiprocessing import Process, Queue
from sklearn.base import ClassifierMixin

import argparse
import json
import signal

import core
from core import EnsembleType
import importance

class QueueLatch:
    def __init__(self, queue):
        self.queue = queue
        self.value = None
        self.get()

    def get(self):
        try:
            self.value = self.queue.get_nowait()
        except QueueEmpty:
            pass
        return self.value

    def wait(self):
        if self.value is None:
            self.value = self.queue.get()
        return self.value
    
class Latch:
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value
    get_wait = get
    def wait(self):
        pass
    
def latch(val_or_queue):
    if isinstance(val_or_queue, queues.Queue):
        return QueueLatch(val_or_queue)
    else:
        return Latch(val_or_queue)

class ControllerKeyError(Exception):
    def __init__(self, key):
        msg = "Process doesn't have input queue called `%s'" % (str(key),)
        super(ControllerKeyError, self).__init__(msg)

class QueueGroup(object):
    def __init__(self, keys):
        self._queues = { kw: Queue() for kw in keys }

    def keys(self):
        return self._queues.keys()
    
    def __setattr__(self, name, value):
        if name != '_queues':
            self._queues[name].put_nowait(value)
            return
        return super(QueueGroup, self).__setattr__(name, value)
        
class SubprocessController(object):
    def __init__(self, func, keywords):
        self.func = func
        self.args = QueueGroup(keywords)
        self.process = None
        self._reset_proc()

    def _reset_proc(self):
        if self.process and self.is_alive:
            self.process.terminate()
        self.process = Process(target=main, kwargs=self.args._queues)

    @property
    def is_alive(self):
        return self.process.is_alive()
    def start(self):
        if self.is_alive: return
        self.process.start()
        
    def stop(self):
        self._reset_proc()
        
class WebAppController(SubprocessController):
    """This class represents the main interface for the web application.
A WebAppController is able to start a web server instance in a separate process,
start/stop the process, and send data to it.

All data communication happens by setting attributes into the dict-like `args' property.
Valid keys are:
    - `aggregate_tree': the `core.AggregateTree' instance which will be visualized by the app;
    - `features_info': a dict (or dict-like) object containing auxiliary informations about the features in the dataset. The recommended way to build this object is through the `collect_features_info' function.
    """
    def __init__(self):
        super(WebAppController, self).__init__(main, ['aggregate_tree', 'features_info'])
        
def main(aggregate_tree, features_info):
    agg_tree = latch(aggregate_tree)
    features_info = latch(features_info)

    print "Waiting for aggregate tree..."
    agg_tree.wait()
    print "done"

    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template('index.html')
    
    @app.route("/tree/nodes/all")
    def get_whole_tree():
        ret = json.dumps(agg_tree.get().query(max_depth=None))
        return ret

    @app.route("/tree/nodes/<node_id>")
    def get_data(node_id):
        max_depth = int(request.args.get('max_depth', 2))
        # print " -- Request: node_id=%s, max_depth=%s" % (node_id, max_depth)

        ret = json.dumps(agg_tree.get().query(node_id, max_depth))
        return ret

    @app.route("/tree/features_info")
    def get_features_info():
        return json.dumps(features_info.get())
    
    @app.route('/coffee/<path:filename>')
    def coffee_src(filename):
        return send_from_directory('./coffee/', filename)

    app.run(host='0.0.0.0', debug=True, use_reloader=False)

def collect_features_info(ensemble, feature_names=None,
                          X_train=None, y_train=None,
                          ensemble_type=None):
    """Assemble a dict of features information from the given dataset and Random Forest regressor/classifier.

    Args:
        ensemble (RandomForestClassifier or RandomForestRegressor):
            The Random Forest predictor from which to extract feature importances.
        feature_names (None or enumerable of str):
            The names of the features, in the order they appear as columns in X_train.
        X_train, y_train (numpy array):
            Training data arrays, data and target, respectively. This
            must be the same data used for the training of `ensemble'.
        ensemble_type (None or core.EnsembleType): 
            When this argument is None, whether `ensemble' is a regressor or
            classifier is automatically inferred. 
            Otherwise, it can be specified, as a core.EnsembleType instance.

    Returns: 
        dict: A dictionary with feature IDs as keys, containing
            the collected feature informations (among this, feature
            importances).
    """
    
    import numpy as np

    if ensemble_type is None:
        if isinstance(ensemble, ClassifierMixin):
            ensemble_type = EnsembleType.classifier
        else:
            ensemble_type = EnsembleType.regressor
            
    if feature_names is None:
        n_features = ensemble.n_features_
        feature_names = [ 'feat_'+str(i+1) for i in range(n_features) ]
    
    features_info = {}
    importance_gini = getattr(ensemble, 'feature_importances_', None)

    importance_oob = None
    if None not in [X_train, y_train]:
        if ensemble_type == EnsembleType.regressor:
            score_func = importance.reg_score
        else:
            score_func = importance.cls_score
        importance_oob = importance.importance(ensemble, X_train, y_train, score_func)
        importance_oob = np.mean(importance_oob, axis=0)

    features_info = { str(index): { 'name': name }
                      for index, name in enumerate(feature_names) }

    if importance_gini is not None:
        for index, name in enumerate(feature_names):
            features_info[str(index)]['importance_gini'] = importance_gini[index]
            
    if importance_oob is not None:
        for index, name in enumerate(feature_names):
            features_info[str(index)]['importance_oob'] = importance_oob[index]

    return features_info

# def get_classifier(df, path, force=False, train_kwargs={}):
#     import data
#     import os
#     OBJ_DIR = path
#     OBJ_FILE = 'objects.pkl'
#     OBJ_PATH = os.path.join(OBJ_DIR, OBJ_FILE)

#     if force or not os.path.exists(OBJ_PATH):
#         kwargs = dict(max_features=[2,3,4])
#         kwargs.update(train_kwargs)
#         rfc = data.train_regressor(df, **kwargs)
#         print " Saving classifier to", OBJ_PATH, "..."
#         if not os.path.exists(OBJ_DIR):
#             os.mkdir(OBJ_DIR)
#         joblib.dump(rfc, OBJ_PATH)
#     else:
#         print "Loading classifers from", OBJ_PATH, "..."
#         rfc = joblib.load(OBJ_PATH)

#     return rfc, df

if __name__ == '__main__':
    from sklearn import ensemble
    from sklearn.externals import joblib
    from sklearn import datasets as ds

    import data
    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true',
                    help="Force re-training classifier "
                    "(as opposed to loading from file)")
    args = ap.parse_args()
    
    # boston = ds.load_digits()
    
    boston = ds.load_boston()
    # rfc = joblib.load('classifier_data_boston/objects.pkl')
    rfc = ensemble.RandomForestRegressor(n_estimators=200)
    rfc.fit(boston.data, boston.target)
    
    print "Data loaded, random forest fitted"
    
    agg = core.AggregateTree(rfc)

    feat_info = collect_features_info(rfc,
                                      feature_names=boston.feature_names,
                                      X_train=boston.data,
                                      y_train=boston.target)
    
    print "Aggregate tree built"
    
    def attach_pdb(sig, frame):
        import pdb
        pdb.Pdb().set_trace(frame)
    signal.signal(signal.SIGUSR1, attach_pdb)

    main(agg, feat_info)


    
