# This code still runs under Python!

# cython: cdivision=True

from __future__ import division
import cython

@cython.locals(x=cython.double)
def f(x):
    # Note: x**4 translates to slow code in Cython
    # Use x*x*x*x to avoid calling 'pow'
    return x**4 - 3 * x

@cython.locals(a=cython.double, b=cython.double,
               N=cython.int, s=cython.double,
               dx=cython.double, i=cython.int)
def integrate_f(a, b, N):
    """Rectangle integration of a function.

    Parameters
    ----------
    a, b : ints
        Interval over which to integrate.
    N : int
        Number of intervals to use in the discretisation.

    """
    s = 0
    dx = (b - a) / N
    for i in range(N):
        s += f(a + i * dx)
    return s * dx

