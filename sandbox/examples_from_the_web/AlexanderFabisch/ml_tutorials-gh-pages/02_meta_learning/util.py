from pylab import *

def plot_classifier(X, y, classifier, label, threshold=0.5):
    # Plot the predictions
    plot_step = 0.02
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = meshgrid(arange(x_min, x_max, plot_step),
                      arange(y_min, y_max, plot_step))
    zz = classifier.predict(c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    if threshold is not None:
        zz = zz > 0.5
    cs = contourf(xx, yy, zz, cmap=cm.Paired)
    axis("tight")

    # Plot the training data
    for i, n, c in zip(range(2), "AB", "br"):
        idx = where(y == i)
        scatter(X[idx, 0], X[idx, 1], c=c, cmap=cm.Paired, label="Class %s" % n)
    setp(gca(), xlim=(x_min, x_max), ylim=(y_min, y_max), title=label)
    legend(loc="upper right")
