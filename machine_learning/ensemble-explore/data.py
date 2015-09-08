import pandas as pd
from sklearn import datasets, ensemble
import time

def dataset_to_dataframe(samples):
    columns = samples.get('feature_names')
    if columns is None:
        n_features = samples['data'].shape[1]
        columns = list('abcdefghijklmnopqrstuwxyz')[:n_features]

    df = pd.DataFrame(samples['data'], columns=columns)
    df['target'] = samples['target']
    return df

def load_linnerud():
    print " -- Loading data (Linnerud)..."
    ds = datasets.load_linnerud()
    print "   features:", ", ".join(ds['feature_names'])
    return dataset_to_dataframe({
        'data': ds['data'],
        'target': ds['target'][:,1]
    })

def load_iris():
    print " -- Loading data (Iris)..."
    return dataset_to_dataframe(datasets.load_iris())

def load_boston():
    print " -- Loading data (Boston)..."
    return dataset_to_dataframe(datasets.load_boston())

def load_diabetes():
    print " -- Loading data (Diabetes)..."
    return dataset_to_dataframe(datasets.load_diabetes())

def generate_dataset(n_samples=600, n_features=6, **kwargs):
    X, y = datasets.make_classification(n_samples=n_samples,
                                        n_features=n_features,
                                        **kwargs)
    
    df = pd.DataFrame(X, columns=list('abcdefghijkl')[:n_features])
    df['target'] = y
    return df

def train(df, cls, **kwargs):
    print " -- Training %s..." % (cls.__name__)

    # The `compute_importances' keyword paramter is (apparently) absent
    # in scikit-learn 0.16.x
    rfc = cls() #compute_importances=False)

    # Here we define the random state to have always the same results
    # Sometimes n_jobs=-1 crashes the kernel, here we use conservatively n_jobs=1
    # params = { 'n_estimators': [50, 100, 200], #[5, 10, 20, 40],
    #            'max_features': [2, 3, 4, 5],
    #            'max_depth': [4, 6, 8],
    #            'min_samples_split': [2, 4],
    #            'min_samples_leaf': [1, 2, 4],
    #            'bootstrap': [True],
    #            'random_state': [0] }
    # params.update(kwargs)
    # t0 = time()
    # grid = grid_search.GridSearchCV(rfc, params, cv=3, n_jobs=2)
    # grid.fit(df.drop('target',axis=1), df['target'])
    # rfc = grid.best_estimator_

    max_features = min(5, len(df.columns)-1)
    rfc = cls(n_estimators=100, max_features=max_features, max_depth=8,
              min_samples_split=2, min_samples_leaf=1, bootstrap=True)
    rfc.fit(df.drop('target',axis=1), df['target'])
    
    print "    Done. Time elapsed:", (time.time() - t0)
    return rfc

def train_regressor(df, **kwargs):
    return train(df, ensemble.RandomForestRegressor, **kwargs)

def train_classifier(df, **kwargs):
    return train(df, ensemble.RandomForestClassifier, **kwargs)

    
