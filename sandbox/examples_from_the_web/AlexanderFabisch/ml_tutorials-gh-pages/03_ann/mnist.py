"""MNIST data set.
"""

import os
import struct
import array
import numpy


def read(digits, dataset="training", path="."):
    """Loads MNIST files into 3D numpy arrays.

    Adapted from: http://abel.ee.ucla.edu/cvxopt/_downloads/mnist.py

    Source: http://g.sweyla.com/blog/2012/mnist-numpy/

    MNIST: http://yann.lecun.com/exdb/mnist/

    **Parameters**
        :digits: list; digits we want to load
        :dataset: string; 'training' or 'testing'
        :path: string; path to the data set files
    """

    if dataset is "training":
        fname_img = os.path.join(path, 'train-images-idx3-ubyte')
        fname_lbl = os.path.join(path, 'train-labels-idx1-ubyte')
    elif dataset is "testing":
        fname_img = os.path.join(path, 't10k-images-idx3-ubyte')
        fname_lbl = os.path.join(path, 't10k-labels-idx1-ubyte')
    else:
        raise ValueError("dataset must be 'testing' or 'training'")

    try:
        flbl = open(fname_lbl, 'rb')
    except IOError:
        raise IOError("Download the MNIST data set from "
                      "http://yann.lecun.com/exdb/mnist/")
    struct.unpack(">II", flbl.read(8))
    lbl = array.array("b", flbl.read())
    flbl.close()

    try:
        fimg = open(fname_img, 'rb')
    except IOError:
        raise IOError("Download the MNIST data set from "
                      "http://yann.lecun.com/exdb/mnist/")
    _, size, rows, cols = struct.unpack(">IIII", fimg.read(16))
    img = array.array("B", fimg.read())
    fimg.close()

    ind = [k for k in xrange(size) if lbl[k] in digits]
    N = len(ind)

    images = numpy.zeros((N, rows, cols), dtype=numpy.uint8)
    labels = numpy.zeros((N, 1), dtype=numpy.int8)
    for i in xrange(len(ind)):
        images[i] = numpy.array(img[ind[i]*rows*cols:
                                (ind[i]+1)*rows*cols]).reshape((rows, cols))
        labels[i] = lbl[ind[i]]

    return images, labels


if __name__ == "__main__":
    import pylab
    images, labels = read([2], "training")
    #pylab.imshow(images.mean(axis=0), cmap=pylab.cm.gray,
    #             interpolation="nearest")
    pylab.imshow(images[0], cmap=pylab.cm.gray, interpolation="nearest")
    pylab.show()
