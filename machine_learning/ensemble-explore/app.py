from __future__ import print_function

from flask import Flask, render_template, send_from_directory
from flask import request
from sklearn.base import ClassifierMixin

import argparse
import json
import signal
import sys
import pickle
import os
import jinja2
from encodings import utf_8

import core
import importance


def run_server(aggregate_tree, features_info, host='0.0.0.0', port=None):
    """Runs the application on a local development web server.  This
    function blocks the thread until the server has finished its
    execution, that is, when it's terminated (either by the user
    typing Ctrl-C, or by sending it a UNIX signal like SIGINT, if
    you're running a UNIX-like OS).

    Args:
        ``aggregate_tree`` (core.AggregateTree):
            The aggregate tree that the app will visualize.

        ``features_info`` (dict):
            a dictionary containing informations about the features in
            the dataset. This should be obtained by calling
            ``collect_features_info``.

        ``host`` (str):
            which hostname to listen on. The default is ``0.0.0.0``,
            meaning the web server will only accept connections from
            the same host the server runs on.

        ``port`` (int or None):
            the TCP port to listen on. Default is 5000, meaning
            you'll be able to reach the application by visiting the URL
            ``http://127.0.0.1:5000/`` with a web browser.
    """

    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template('index.html', is_standalone=False)

    @app.route("/tree/nodes/all")
    def get_whole_tree():
        res = json.dumps(aggregate_tree.query(max_depth=None))
        return res

    @app.route("/tree/nodes/<node_id>")
    def get_data(node_id):
        max_depth = int(request.args.get('max_depth', 2))
        res = json.dumps(aggregate_tree.query(node_id, max_depth))
        return res

    @app.route("/tree/features_info")
    def get_features_info():
        return json.dumps(features_info)

    @app.route('/coffee/<path:filename>')
    def coffee_src(filename):
        return send_from_directory('./coffee/', filename)

    app.run(host='0.0.0.0', debug=True, use_reloader=False)


def assemble_standalone(aggregate_tree, features_info, out_dir,
                        app_root=None):
    """Assembles a standalone version of the application.

    After execution, the directory ``out_dir`` will contain all the
    files needed for the web app to run without a backing web server
    ("standalone"). These files included encoded data, HTML and CSS
    files.  To execute the app, use a web browser to open the
    ``index.html`` file inside the directory indicated by ``out_dir``.

    If the ``out_dir`` directory doesn't exists, it is created
    (recursively).

    Args:
        ``aggregate_tree`` (core.AggregateTree):
            The aggregate tree that the app will visualize.

        ``features_info`` (dict):
            a dictionary containing informations about the features in
            the dataset. This should be obtained by calling
            ``collect_features_info``.

        ``out_dir`` (str):
            Directory into which the application files are collected.

        ``app_root`` (str):
            The app's root directory. Default is the directory of this
            module.

    Returns: None

    """

    if app_root is None:
        this_file_abs = os.path.abspath(__file__)
        app_root = os.path.dirname(this_file_abs)

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    # Encode data in JSON
    tree = aggregate_tree.query(max_depth=None)
    tree_json = json.dumps(tree, indent=2)
    features_info_json = json.dumps(features_info, indent=2)

    # Configure Jinja2 to correctly locate the templates
    templ_path = os.path.join(app_root, 'templates')
    templ_loader = jinja2.FileSystemLoader(templ_path)
    templ_env = jinja2.Environment(loader=templ_loader)

    templ_vars = {
        'is_standalone': True,
        'tree': tree_json,
        'features_info': features_info_json
    }

    # I've chosen to implement the static application by textually including
    # the file dependencies right in the HTML, so that the app is composed
    # of a single, self-contained HTML file. That makes it easier to embed
    # the app, for example in an iframe that sits in a Jupyter notebook.

    # The file 'data_loader_standalone.js' is also included, but
    # through an {% include %} directive in the template instead of
    # here.  It's worth noting that that file is also a Jinja
    # template, which textually include, in JSON format, the data we
    # give to it here. Fucking sucks, right?  Well, as it happens,
    # Chrome prevents pages from loading files from "file://" URLs. So
    # writing our data in separate JSON files would only work properly
    # in Firefox and other browsers which don't implement that
    # policy. At the moment, embedding the JSON in the JS is the
    # simplest way that I can think of to solve this problem, and I
    # don't think it poses a threat to security. Also, the same
    # rationale for including all the JS and CSS in the HTML also
    # (kinda) applies to the data.

    included_files = {
        'stylesheet': 'ensemble-explore/static/style.css',
        'font_awesome': 'ensemble-explore/static/font-awesome-4.3.0/css/font-awesome.min.css',
        'javascript': 'ensemble-explore/static/app.js'
    }

    #print(os.getcwd())
    for varname, filename in included_files.iteritems():
        with open(filename) as f:
            templ_vars[varname] = f.read().decode('utf_8')

    index = templ_env.get_template('index.html')
    index_html = index.render(**templ_vars)
    index_html_path = os.path.join(out_dir, 'index.html')
    with open(index_html_path, 'wb') as f:
        f.write(index_html.encode('utf_8'))


def collect_features_info(ensemble, feature_names=None,
                          X_train=None, y_train=None,
                          ensemble_type=None):
    """Assemble a dict of features information from the given dataset and
    Random Forest regressor/classifier.

    Args:
        ensemble (RandomForestClassifier or RandomForestRegressor):
            The Random Forest predictor from which to extract feature
            importances.
        feature_names (None or enumerable of str):
            The names of the features, in the order they appear as
            columns in X_train.
        X_train, y_train (numpy array):
            Training data arrays, data and target, respectively. This
            must be the same data used for the training of `ensemble'.
        ensemble_type (None or core.EnsembleType):
            When this argument is None, whether `ensemble' is a
            regressor or classifier is automatically inferred.
            Otherwise, it can be specified, as a core.EnsembleType
            instance.

    Returns (dict):
        dictionary with feature IDs as keys, containing the collected
        feature informations (among this, feature importances).

    """

    import numpy as np

    if ensemble_type is None:
        if isinstance(ensemble, ClassifierMixin):
            ensemble_type = core.EnsembleType.classifier
        else:
            ensemble_type = core.EnsembleType.regressor

    if feature_names is None:
        n_features = ensemble.n_features_
        feature_names = ['feat_'+str(i+1) for i in range(n_features)]

    features_info = {}
    importance_gini = getattr(ensemble, 'feature_importances_', None)

    importance_oob = None
    if X_train is not None and y_train is not None:
        if ensemble_type == core.EnsembleType.regressor:
            score_func = importance.reg_score
        else:
            score_func = importance.cls_score
        importance_oob = importance.importance(ensemble, X_train, y_train,
                                               score_func)
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


def main_cli():
    from sklearn import ensemble
    from sklearn.externals import joblib
    from sklearn import datasets as ds

    import data

    ap = argparse.ArgumentParser()
    ap.add_argument('--force', action='store_true',
                    help="Force re-training classifier "
                    "(as opposed to loading from file)")
    ap.add_argument('--load', metavar='filename',
                    dest='load_filename',
                    help="Restore previously saved data from given "
                    "file. No computation happens during the program.")
    ap.add_argument('--save', metavar='filename',
                    dest='save_filename',
                    help="Save computed data on a file, for later use "
                    "(--load)")

    args = ap.parse_args()

    if args.load_filename and args.save_filename:
        print("{}: error: The --save and --load options are mutually exclusive."
              .format(sys.argv[0]))
        return

    if args.load_filename:
        with open(args.load_filename) as f:
            file_data = pickle.load(f)

        agg = file_data['aggregate_tree']
        feat_info = file_data['features_info']
        print("Random forest, aggregate tree loaded")

    else:
        # This is where data is loaded, when the user hasn't specified
        # the --load option. Change the following line to change which
        # dataset is used to build the Random Forest. You can also
        # change RandomForestRegressor to RandomForestClassifier

        # boston = ds.load_digits()
        boston = ds.load_boston()
        # rfc = joblib.load('classifier_data_boston/objects.pkl')
        rfc = ensemble.RandomForestRegressor(n_estimators=200)
        rfc.fit(boston.data, boston.target)

        print("Data loaded, random forest fitted")

        agg = core.AggregateTree(rfc)
        feat_info = collect_features_info(
            ensemble=rfc,
            feature_names=boston.feature_names,
            X_train=boston.data,
            y_train=boston.target)

        print("Random forest, aggregate tree built")

    @signal.signal(signal.SIGUSR1)
    def attach_pdb(sig, frame):
        import pdb
        pdb.Pdb().set_trace(frame)

    if args.save_filename:
        file_data = {
            'aggregate_tree': agg,
            'features_info': feat_info
        }

        with open(args.save_filename, 'w') as f:
            pickle.dump(file_data, f)

    run_server(aggregate_tree=agg,
               features_info=feat_info)

if __name__ == '__main__':
    main_cli()
