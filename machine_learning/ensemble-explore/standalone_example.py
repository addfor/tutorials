#!/usr/bin/env python2

from sklearn.ensemble import RandomForestRegressor
from sklearn import datasets as ds

import core
import app

boston = ds.load_boston()
rfr = RandomForestRegressor(n_estimators=200)
rfr.fit(boston.data, boston.target)

print "Building aggregate tree..."
agg = core.AggregateTree(rfr)

print "Collecting features info..."
features = app.collect_features_info(
    ensemble=rfr,
    X_train=boston.data,
    y_train=boston.target)

print "Assembling standalone app..."
app.assemble_standalone(agg, features,
                        out_dir='somewhere/standalone/app')
