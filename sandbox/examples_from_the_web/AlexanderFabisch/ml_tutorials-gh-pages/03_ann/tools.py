"""Helper functions for artificial neural networks.
"""

import numpy
import scipy.weave


def softmax(a):
    """Softmax activation function.

    The outputs will be interpreted as probabilities and thus have to
    lie within [0, 1] and must sum to unity:

    .. math::

        g(a_f) = \\frac{\\exp(a_f)}{\\sum_F \\exp(a_F)}.

    To avoid numerical problems, we substract the maximum component of
    :math:`a` from all of its components before we calculate the output. This
    is mathematically equivalent.

    **Parameters**
        :a: array-like, shape = [F,]; activations

    **Returns**
        :y: array-like, shape = [F,]; outputs
    """
    y = numpy.exp(a - a.max())
    return y / y.sum()


def linear_derivative(y):
    """Derivative of linear activation function.

    **Parameters**
        :y: array-like, shape = [F,]; outputs (g(a))

    **Returns**
        :gd(y): array-like, shape = [F,]; derivatives (gdot(a))
    """
    return 1


def relu(a):
    """Non-saturating activation function: Rectified Linar Unit (ReLU).

    Max-with-zero nonlinearity: :math:`max(0, a)`.

    **Parameters**
        :a: array-like, shape = [F,]; activations

    **Returns**
        :y: array-like, shape = [F,]; outputs
    """
    return numpy.max([numpy.zeros_like(a), a], axis=0)


def relu_derivative(y):
    """Derivative of ReLU activation function.

    **Parameters**
        :y: array-like, shape = [F,]; outputs (g(a))

    **Returns**
        :gd(y): array-like, shape = [F,]; derivatives (gdot(a))
    """
    return numpy.sign(y)


def scale(x):
    """Scales values to [-1, 1].

    **Parameters**
        :x: array-like, shape = arbitrary; unscaled data

    **Returns**
        :x_scaled: array-like, shape = x.shape; scaled data
    """
    minimum = x.min()
    return 2.0 * (x - minimum) / (x.max() - minimum) - 1.0


def generate_targets(labels):
    """1-of-c category encoding (c is the number of categories/classes).

    **Parameters**
        :labels: array-like, shape = [N, 1]; class labels (0 to c)

    **Returns**
        :targets: array-like, shape = [N, c]; target matrix with 1-of-c
                                              encoding
    """
    N = len(labels)
    classes = labels.max() + 1
    targets = numpy.zeros((N, classes))
    for n in range(N):
        targets[n, labels[n]] = 1.0
    return targets


def model_accuracy(model, X, labels):
    """Compute accuracy of the model on data set.

    **Parameters**
        :model: Model; learned model (has to support the predict function)
        :X: array-like, shape = [N, D]; inputs (scaled to [-1, 1])
        :labels: array-like, shape = [N, 1]; class labels (lie within [0, c-1])

    **Returns**
        :accuracy: float; fraction of correct predicted labels, range [0, 1]
    """
    predicted = numpy.argmax(model.predict(X), axis=1)[:, None]
    return float((predicted == labels).sum()) / len(labels)


def convolve(feature_maps, kernels, bias, stride_y=1, stride_x=1,
             compiler="gcc"):
    """Convolve I 2-dimensional feature maps to generate J output feature maps.

    **Parameters**
        :feature_maps: array-like, shape = [I, Y, X]; input feature maps
        :kernels: array-like, shape = [J, I, Y_k, X_k]; filter kernels
        :bias: array-like, shape = [J, I]; bias matrix
        :stride_y: int, optional; column step size
        :stride_x: int, optional; row step size
        :compiler: string, optional; C compiler to compile the accelerated
                                     convolution code

    **Returns**
        :a: array-like, shape = [J, Y-2*floor(Y_k/2)/stride_y,
                                 X-2*floor(X_k/2)/stride_x]; convolved feature maps
    """
    I = feature_maps.shape[0]
    Y = feature_maps.shape[1]
    X = feature_maps.shape[2]
    J = kernels.shape[0]
    assert I == kernels.shape[1]
    Y_k = kernels.shape[2]
    X_k = kernels.shape[3]
    Y_o = (Y-2*(Y_k/2))/stride_y
    X_o = (X-2*(X_k/2))/stride_x
    a = numpy.zeros((J, Y_o, X_o))

    code = \
        """
        for(int j = 0; j < J; j++)
        {
            for(int i = 0; i < I; i++)
            {
                for(int yo = 0, yi = 0; yo < Y_o; yo++, yi+=stride_y)
                {
                    for(int xo = 0, xi = 0; xo < X_o; xo++, xi+=stride_x)
                    {
                        register double tmp = bias(j, i);
                        for(int yk = 0, xik = xi; yk < Y_k; yk++, xik++)
                            for(int xk = 0, yik = yi; xk < X_k; xk++, yik++)
                                tmp += feature_maps(i, yik, xik) *
                                    kernels(j, i, yk, xk);
                        a(j, yo, xo) += tmp;
                    }
                }
            }
        }
        """
    variables = ["J", "I", "Y_o", "X_o", "stride_x", "stride_y", "Y_k", "X_k",
                 "feature_maps", "kernels", "bias", "a"]

    scipy.weave.inline(code, variables,
                       type_converters=scipy.weave.converters.blitz,
                       compiler=compiler)
    return a


def back_convolve(feature_maps, kernels, bias, deltas, stride_y=1, stride_x=1,
                  compiler="gcc"):
    """Convolve I 2-dimensional feature_maps to generate J output feature_maps.

    **Parameters**
        :feature_maps: array-like, shape = [I, Y, X]; input feature maps
        :kernels: array-like, shape = [J, I, Y_k, X_k]; filter kernels
        :bias: array-like, shape = [J, I]; bias matrix
        :deltas: array-like, shape = [J, Y-2*floor(Y_k/2)/stride_y,
                                      X-2*floor(X_k/2)/stride_x]; deltas
        :stride_y: int, optional; column step size
        :stride_x: int, optional; row step size
        :compiler: string, optional; C compiler to compile the accelerated
                                     convolution code

    **Returns**
        :der: array-like, shape = [J, I, Y_k, X_k]; filter kernel derivatives
        :derb: array-like, shape = [J, I]; bias derivatives
        :e: array-like, shape = [I, Y, X]; errors
    """
    I = feature_maps.shape[0]
    Y = feature_maps.shape[1]
    X = feature_maps.shape[2]
    J = kernels.shape[0]
    assert I == kernels.shape[1]
    Y_k = kernels.shape[2]
    X_k = kernels.shape[3]
    Y_o = (Y-2*(Y_k/2))/stride_y
    X_o = (X-2*(X_k/2))/stride_x

    der = numpy.zeros_like(kernels)
    derb = numpy.zeros_like(bias)
    e = numpy.zeros_like(feature_maps)

    code = \
        """
        for(int j = 0; j < J; j++)
        {
            for(int i = 0; i < I; i++)
            {
                for(int yo = 0, yi = 0; yo < Y_o; yo++, yi+=stride_y)
                {
                    for(int xo = 0, xi = 0; xo < X_o; xo++, xi+=stride_x)
                    {
                        for(int yk = 0, xik = xi; yk < Y_k; yk++, xik++)
                        {
                            for(int xk = 0, yik = yi; xk < X_k; xk++, yik++)
                            {
                                e(i, yik, xik) += kernels(j, i, yk, xk) *
                                        deltas(j, yo, xo);
                                der(j, i, yk, xk) += deltas(j, yo, xo) *
                                        feature_maps(i, yik, xik);
                            }
                        }
                        derb(j, i) += deltas(j, yo, xo);
                    }
                }
            }
        }
        """
    variables = ["J", "I", "Y_o", "X_o", "stride_x", "stride_y", "Y_k", "X_k",
                 "kernels", "feature_maps", "deltas", "der", "derb", "e"]

    scipy.weave.inline(code, variables,
                       type_converters=scipy.weave.converters.blitz,
                       compiler=compiler)
    return der, derb, e
