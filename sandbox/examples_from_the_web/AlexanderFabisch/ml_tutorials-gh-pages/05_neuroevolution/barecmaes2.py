#!/usr/bin/env python
"""Module barecmaes2 implements the CMA-ES without using `numpy`.  

The Covariance Matrix Adaptation Evolution Strategy, CMA-ES, serves for nonlinear function minimization. 

The **main functionality** is implemented in

  - class `Cmaes` and
  - function `fmin()` that is a single-line-usage wrapper around `Cmaes`.

This code has two **purposes**: 

1. it might be used for READING and UNDERSTANDING the basic flow and the details
   of the CMA-ES *algorithm*. The source code is meant to be read. For short,
   study the class `Cmaes`, in particular its doc string and the code of the  
   method `Cmaes.tell()`, where all the real work is done in about 20 lines 
   (see "def tell" in the source). Otherwise, reading from the top is a feasible
   option.
2. it might be used when the python module `numpy` is not available. 
   When `numpy` is available, rather use `cma.py` 
   (see http://www.lri.fr/~hansen/cmaes_inmatlab.html#python) to run 
   serious simulations: the latter code has many more lines, but executes
   much faster (roughly ten times), offers a richer user interface, far better 
   termination options, supposedly quite useful output, and automatic 
   restarts.
    
Dependencies: `math.exp`, `math.log` and `random.normalvariate` (modules `matplotlib.pylab` 
and `sys` are optional). 

Testing: call ``python barecmaes2.py`` at the OS shell. Tested with 
Python 2.5 (only with removed import of print_function), 2.6, 2.7, 3.2. 
Small deviations between the versions are expected. 

URL: http://www.lri.fr/~hansen/barecmaes2.py

Last change: June, 2011, version 1.11

:Author: Nikolaus Hansen, 2010-2011, hansen[at-symbol]lri.fr
:License: This code is released into the public domain (that is, you may 
    use and modify it however you like). 

"""
# import future syntax like for Python version >= 3.0
from __future__ import division  # such that 0 != 1/2 == 0.5, like with python -Qnew
from __future__ import print_function  # available since 2.6, out-comment for 2.5

from math import log, exp
from random import normalvariate as random_normalvariate  # see randn keyword argument to Cmaes.__init__

# Optional imports, can be outcommented, if not available
try: 
    import sys
    import matplotlib.pylab as pylab # for plotting, scitools.easyfiz might be an alternative
except: 
    pass  # print '  pylab could not be imported  '
    
__docformat__ = "reStructuredText"


def abstract():
    """marks a method as abstract, ie to be implemented by a subclass"""
    raise NotImplementedError('method must be implemented in subclass')

def fmin(objectivefct, xstart, sigma, stopeval='1e3*N**2', ftarget=None, verb_disp=20, verb_log=1, verb_plot=100):  
    """non-linear non-convex minimization procedure. 
    The functional interface to CMA-ES. 
    
    Parameters
    ==========
        `objectivefct` 
            a function that takes as input a list of floats (like [3.0, 2.2, 1.1])
            and returns a single float (a scalar). A minimum is searched for. 
        `xstart`
            list of numbers (like `[3,2,1.2]`), initial solution vector
        `sigma` 
            float, initial step-size (standard deviation in each coordinate)
        `ftarget`
            float, target function value
        `stopeval`
            int or str, maximal number of function evaluations, a string is 
            evaluated with N being the search space dimension
        `verb_disp`
            int, display on console every verb_disp iteration, 0 for never
        `verb_log`
            int, data logging every verb_log iteration, 0 for never 
        `verb_plot`
            int, plot logged data every verb_plot iteration, 0 for never
            
    Returns
    =======
    ``return es.result() + (es.stop(), es, logger)``, that is, 
    ``(xbest, fbest, evalsbest, evals, iterations, xmean, termination_condition, Cmaes_object_instance, data_logger)`` 
 
    Example
    =======
    The following example minimizes the function `Fcts.elli`:: 
     
        >> import barecmaes2 as cma
        >> res = cma.fmin(cma.Fcts.elli, 10 * [0.5], 0.3, verb_disp=100)
        evals: ax-ratio max(std)   f-value
           10:     1.0  2.8e-01  198003.585517
         1000:     8.4  5.5e-02  95.9162313173
         2000:    40.5  3.6e-02  5.07618122556
         3000:   149.1  8.5e-03  0.271537247667
         4000:   302.2  4.2e-03  0.0623570374451
         5000:   681.1  5.9e-03  0.000485971681802
         6000:  1146.4  9.5e-06  5.26919100476e-10
         6510:  1009.1  2.3e-07  3.34128914738e-13
        termination by {'tolfun': 1e-12}
        best f-value = 3.34128914738e-13
        
        >> print res[0]
        [2.1187532328944602e-07, 6.893386424102321e-08, -2.008255256456535e-09, 4.472078873398156e-09, -9.421306741003398e-09, 7.331265238205156e-09, 2.4804701814730273e-10, -6.030651566971234e-10, -6.063921614755129e-10, -1.066906137937511e-10]

        >> print res[1]
        3.34128914738e-13

        >> res[-1].plot()  # needs pylab/matplotlib to be installed
        
    Details
    =======
    By default `fmin()` tries to plot some output. This works only with Python 
    module `matplotlib` being installed. The two lines::
    
        res = cma.fmin(cma.Fcts.elli, 10 * [0.5], 0.3, verb_plot=0)
        res = cma.Cmaes(10 * [0.5], 0.3).optimize(cma.Fcts.elli, cma.CmaesDataLogger())
        
    do the same. `fmin()` adds the possibility to plot *during* the execution. 
            
    :See: `Cmaes`, `OOOptimizer`
    
    """
    es = Cmaes(xstart, sigma, stopeval, ftarget)  # new optimizer instance
    logger = CmaesDataLogger(verb_log).add(es, True)  # new data instance, added data of iteration 0
    while not es.stop():  # iterate the optimizer 
        X = es.ask()  # get new candidate solution
        fitvals = [objectivefct(x) for x in X]  # evaluate solutions
        es.tell(X, fitvals)  # all the real work is done here
        
        # bookkeeping and display
        es.disp(verb_disp)  # display something once in a while
        logger.add(es)      # append data, could become expensive for long runs
        if verb_plot and es.counteval/es.lam % verb_plot == 0:
            logger.plot()
    
    # final display
    if verb_disp:
        es.disp(1)    
        print('termination by', es.stop())
        print('best f-value =', es.result()[1])
        print('solution =', es.result()[0])
    logger.add(es, True) if verb_log else None
    logger.plot() if verb_plot else None
        
    return es.result() + (es.stop(), es, logger)

class OOOptimizer(object): 
    """"abstract" base class for an OO optimizer interface. 
    """
    def __init__(self, xstart, **more_args): 
        """abstract method, ``xstart`` is a mandatory argument """ 
        abstract()
    def ask(self): 
        """abstract method, AKA get, deliver new candidate solution(s), a list of "vectors" """
        abstract()
    def tell(self, solutions, function_values): 
        """abstract method, AKA update, prepare for next iteration"""
        abstract() 
    def stop(self): 
        """abstract method, return satisfied termination conditions in a dictionary like 
        ``{'termination reason':value, ...}``, for example ``{'tolfun':1e-12}``, or the empty 
        dictionary ``{}``. The implementation of `stop()` should prevent an infinite loop. """ 
        abstract()
    def result(self): 
        """abstract method, return ``(x, f(x), ...)``, that is the minimizer, its function value, ..."""
        abstract()
    def disp(self, verbosity_modulo=1):
        """display of some iteration info"""
        print("method disp of " + str(type(self)) + " is not implemented")
    def optimize(self, objectivefct, logger=None, verb_disp=20, iterations=None):
        """iterate over ``OOOptimizer self`` using objective function ``objectivefct`` with 
        verbosity ``verb_disp``, using ``OptimDataLogger logger`` with at most ``iterations`` 
        iterations and return ``self.result() + (self.stop(), self, logger)``.
         
        Example
        =======
        ::

            import barecmaes2 as cma
            res = cma.Cmaes(7 * [0.1], 0.5).optimize(cma.Fcts.rosenbrock) 
            print res[0]
            
        """
        iter = 0
        while not self.stop():
            if iterations is not None and iter >= iterations:
                return self.result()
            iter += 1

            X = self.ask()         # deliver candidate solutions
            fitvals = [objectivefct(x) for x in X]
            self.tell(X, fitvals)  # all the work is done here

            self.disp(verb_disp)
            logger.add(self) if logger else None
        
        logger.add(self, True)  if logger else None 
        if verb_disp:
            self.disp(1)    
            print('termination by', self.stop())
            print('best f-value =', self.result()[1])
            print('solution =', self.result()[0])

        return self.result() + (self.stop(), self, logger)

class Cmaes(OOOptimizer):  
    """class for non-linear non-convex minimization. The class implements the 
    interface define in `OOOptimizer`, namely the methods `__init__()`, `ask()`, 
    `tell()`, `stop()`, `result()`, and `disp()`.   
        
    Examples
    --------
    All examples minimize the function `elli`, the output is not shown. 
    (A preferred environment to execute all examples is ``ipython -pylab``.) 
    First we need to :: 
    
        import barecmaes2 as cma

    The shortest example uses the inherited method `OOOptimizer.optimize()`:: 
        
        res = cma.Cmaes(8 * [0.1], 0.5).optimize(cma.Fcts.elli)
    
    See method `__init__()` for the input parameters to `Cmaes`. We might have 
    a look at the result::
    
        print res[0]  # best solution and 
        print res[1]  # its function value
    
    `res` is the return value from method `Cmaes.results()` appended with `None` (no logger). 
    In order to display more exciting output we rather do ::
    
        logger = cma.CmaesDataLogger()
        res = cma.Cmaes(9 * [0.5], 0.3).optimize(cma.Fcts.elli, logger)
        logger.plot()  # if matplotlib is available, logger == res[-1]

    or even shorter ::
     
        res = cma.Cmaes(9 * [0.5], 0.3).optimize(cma.Fcts.elli, cma.CmaesDataLogger())
        res[-1].plot()  # if matplotlib is available
              
    Virtually the same example can be written with an explicit loop instead of using 
    `optimize()`. This gives the necessary insight into the `Cmaes` class interface
    and gives entire control over the iteration loop:: 
     
        optim = cma.Cmaes(9 * [0.5], 0.3)  # a new Cmaes instance calling Cmaes.__init__()
        logger = cma.CmaesDataLogger().register(optim)  # get a logger instance
 
        # this loop resembles optimize() 
        while not optim.stop(): # iterate
            X = optim.ask()     # get candidate solutions
            #  do whatever needs to be done, however rather don't 
            #  change X unless like for example X[2] = optim.ask()[0]
            f = [cma.Fcts.elli(x) for x in X]  # evaluate solutions
            optim.tell(X, f)    # do all the real work: prepare for next iteration
            optim.disp(20)      # display info every 20th iteration
            logger.add()        # log another "data line"
 
        # final output
        print('termination by', optim.stop())
        print('best f-value =', optim.result()[1])
        print('best solution =', optim.result()[0])
        
        print('potentially better solution xmean =', optim.result()[5])
        print('let\'s check f(xmean) =', cma.Fcts.elli(optim.result()[5])) 
        logger.plot()  # if matplotlib is available
        raw_input('press enter to continue')  # prevents exiting and closing figures 
    
    A slightly longer example, which also plots within the loop, is 
    the implementation of function `fmin(...)`. 
    
    Details
    -------
    Most of the work is done in the method `tell(...)`. The method `result()` returns more useful output. 
         
    :See: `fmin()`, `OOOptimizer.optimize()`
    
    """
    def __init__(self, xstart, sigma, # mandatory
                 stopeval='1e3*N**2', ftarget=None, 
                 popsize="4 + int(3 * log(N))", 
                 randn=random_normalvariate):
        """Initialize` Cmaes` object instance, the first two arguments are mandatory.
         
        Parameters
        ----------
            - `xstart` -- ``list`` of numbers (like ``[3, 2, 1.2]``), initial solution vector
            - `sigma` -- ``float``, initial step-size (standard deviation in each coordinate)
            - `stopeval` -- ``int`` or ``str``, maximal number of function evaluations, a string is 
                evaluated with ``N`` being the search space dimension
            - `ftarget` -- `float`, target function value
            - `randn` -- normal random number generator, by default random.normalvariate
        
        """
        # process input parameters
        N = len(xstart)            # number of objective variables/problem dimension
        self.xmean = xstart[:]     # objective variables initial point, a copy
        self.sigma = sigma
        self.stopfitness = ftarget # stop if fitness < stopfitness (minimization)
        self.stopeval = eval(stopeval) if type(stopeval) is type("") else stopeval
        self.randn = randn
        
        # Strategy parameter setting: Selection  
        self.lam = eval(popsize) if type(popsize) is type("") else popsize  # population size, offspring number
        self.mu = int(self.lam / 2)  # number of parents/points for recombination
        self.weights = [log(self.mu+0.5) - log(i+1) for i in range(self.mu)]  # recombination weights
        self.weights = [w / sum(self.weights) for w in self.weights]  # normalize recombination weights array
        self.mueff = sum(self.weights)**2 / sum(w**2 for w in self.weights) # variance-effectiveness of sum w_i x_i
    
        # Strategy parameter setting: Adaptation
        self.cc = (4 + self.mueff/N) / (N+4 + 2 * self.mueff/N)  # time constant for cumulation for C
        self.cs = (self.mueff + 2) / (N + self.mueff + 5)  # t-const for cumulation for sigma control
        self.c1 = 2 / ((N + 1.3)**2 + self.mueff)     # learning rate for rank-one update of C
        self.cmu = min([1 - self.c1, 2 * (self.mueff - 2 + 1/self.mueff) / ((N + 2)**2 + self.mueff)])  # and for rank-mu update
        self.damps = 2 * self.mueff/self.lam + 0.3 + self.cs  # damping for sigma, usually close to 1
    
        # Initialize dynamic (internal) state variables 
        self.pc = N * [0];  self.ps = N * [0]  # evolution paths for C and sigma
        self.B = eye(N)   # B defines the coordinate system 
        self.D = N * [1]  # diagonal D defines the scaling
        self.C = eye(N)   # covariance matrix 
        self.invsqrtC = eye(N)  # C^-1/2 
        self.eigeneval = 0      # tracking the update of B and D
        self.counteval = 0  

        self.best = BestSolution()
        
    def stop(self):
        """return satisfied termination conditions in a dictionary like 
        {'termination reason':value, ...}, for example {'tolfun':1e-12}, 
        or the empty dict {}""" 
        res = {}
        if self.counteval > 0: 
            if self.counteval >= self.stopeval:
                res['evals'] = self.stopeval
            if self.stopfitness is not None and len(self.fitvals) > 0 and self.fitvals[0] <= self.stopfitness:
                res['ftarget'] = self.stopfitness
            if max(self.D) > 1e7 * min(self.D):
                res['condition'] = 1e7
            if len(self.fitvals) > 1 and self.fitvals[-1] - self.fitvals[0] < 1e-12:
                res['tolfun'] = 1e-12 
            if self.sigma * max(self.D) < 1e-11:  # max(diag(C))**0.5 < max(D) 
                res['tolx'] = 1e-11
        return res

    def ask(self):
        """return a list of lambda candidate solutions according to 
        m + sig * Normal(0,C) = m + sig * B * D * Normal(0,I)"""

        # Eigendecomposition: first update B, D and invsqrtC from C, if necessary  
        if self.counteval - self.eigeneval > self.lam/(self.c1+self.cmu)/len(self.C)/10:  # to achieve O(N**2)
            self.eigeneval = self.counteval
            self.D, self.B = eig(self.C)       # eigen decomposition, B==normalized eigenvectors, O(N**3)
            self.D = [d**0.5 for d in self.D]  # D contains standard deviations now
            iN = range(len(self.C))
            for i in iN:                       # compute invsqrtC = C**(-1/2) = B D**(-1/2) B'
                for j in iN: 
                    self.invsqrtC[i][j] = sum(self.B[i][k] * self.B[j][k] / self.D[k] for k in iN) 

        # lam vectors x_k = m  +          sigma *         B *  D * randn_k(N)         
        return [plus(self.xmean, dot1(self.sigma, dot(self.B, [d * self.randn(0,1) for d in self.D]))) 
               for k in range(self.lam) if k > -1]  # repeat lam times and prevent warning 
        
    def tell(self, arx, fitvals):
        """update the evolution paths and the distribution parameters m, sigma, and C within CMA-ES. 
        
        Parameters
        ----------
            `arx` 
                a list of solutions, presumably from `ask()`
            `fitvals` 
                the corresponding objective function values
        
        """
        
        # bookkeeping, preparation
        self.counteval += len(fitvals)  # slightly artificial to do this here
        N = len(self.xmean)             # convenience short cuts
        iN = range(N)  
        xold = self.xmean               # keep previous mean to compute Deltas
        
        # Sort by fitness and compute weighted mean into xmean
        self.fitvals, arindex = sorted(fitvals), argsort(fitvals)  # minimization
        arx = [arx[arindex[k]] for k in range(self.mu)]  # sorted arx
        del fitvals, arindex  # prevent misuse, also self.fitvals is kept for termination and display only
        self.best.update([arx[0]], [self.fitvals[0]], self.counteval)
        
        # xmean = [x_1=best, x_2, ..., x_mu] * weights
        self.xmean = dot(arx[0:self.mu], self.weights, t=True)  # recombination, new mean value
        #         == [sum(self.weights[k] * arx[k][i] for k in range(self.mu)) for i in iN]
        
        # Cumulation: update evolution paths
        y = minus(self.xmean, xold)
        z = dot(self.invsqrtC, y)  # == C**(-1/2) * (xnew - xold)
        
        c = (self.cs * (2-self.cs) * self.mueff)**0.5 / self.sigma  # normalizing coefficient 
        for i in iN:
            self.ps[i] += -self.cs * self.ps[i] + c * z[i]  # exponential decay on ps
        hsig = sum(x**2 for x in self.ps) / (1-(1-self.cs)**(2*self.counteval/self.lam)) / N < 2 + 4./(N+1) 
        c = (self.cc * (2-self.cc) * self.mueff)**0.5 / self.sigma  # normalizing coefficient
        for i in iN:
            self.pc[i] += -self.cc * self.pc[i] + c * hsig * y[i]  # exponential decay on pc
        
        # Adapt covariance matrix C
        c1a = self.c1 - (1-hsig**2) * self.c1 * self.cc * (2-self.cc)  # minor adjustment for variance loss by hsig
        for i in iN:
            for j in iN:
                Cmuij = sum(self.weights[k] * (arx[k][i]-xold[i]) * (arx[k][j]-xold[j]) for k in range(self.mu)
                           ) / self.sigma**2  # rank-mu update
                self.C[i][j] += (-c1a-self.cmu) * self.C[i][j] + self.c1 * self.pc[i]*self.pc[j] + self.cmu * Cmuij

        # Adapt step-size sigma with factor <= exp(0.6) \approx 1.82
        self.sigma *= exp(min(0.6, (self.cs/self.damps) * (sum(x**2 for x in self.ps) / N - 1) / 2)) 
        # self.sigma *= exp(min(0.6, (self.cs/self.damps) * ((sum(x**2 for x in self.ps) / N)**0.5/(1-1./(4.*N)+1./(21.*N**2)) - 1)))
        
    def result(self):
        """return (xbest, f(xbest), evaluations_xbest, evaluations, iterations, xmean)"""
        return self.best.get() + (self.counteval, int(self.counteval/self.lam), self.xmean)
        
    def disp(self, verb_modulo=1):
        """display some iteration info"""
        iteration = self.counteval / self.lam 

        if iteration == 1 or iteration % (10*verb_modulo) == 0:
            print('evals: ax-ratio max(std)   f-value')
        if iteration <= 2 or iteration % verb_modulo == 0:
            print(repr(self.counteval).rjust(5) + ': ' +
                    ' %6.1f %8.1e  ' % (max(self.D) / min(self.D), self.sigma*max([self.C[i][i] for i in range(len(self.C))])**0.5) + 
                    str(self.fitvals[0]))
            try:
                sys.stdout.flush()
            except:
                pass
        return None

# -----------------------------------------------
class BestSolution(object):
    """container to keep track of the best solution seen"""
    def __init__(self, x=None, f=None, evals=None):
        """take `x`, `f`, and `evals` to initialize the best solution. The
        better solutions have smaller `f`-values. """
        self.x, self.f, self.evals = x, f, evals
    def update(self, arx, arf, evals=None):
        """initialize the best solution with `x`, `f`, and `evals`.
        Better solutions have smaller `f`-values.""" 
        if self.f is None or min(arf) < self.f:
            i = arf.index(min(arf))
            self.x, self.f = arx[i], arf[i]
            self.evals = None if not evals else evals - len(arf) + i + 1
        return self
    def get(self):
        """return ``(x, f, evals)`` """
        return self.x, self.f, self.evals

# -----------------------------------------------
class OptimDataLogger(object):
    """"abstract" base class for a data logger that can be used with an `OOOptimizer`"""
    def register(self, optim):
        self.optim = optim
        return self
    def add(self, optim=None, force=False):
        """abstract method, add a "data point" from the state of optim into the logger"""
        abstract()
    def disp(self):
        """display some data trace (not implemented)"""
        print('method OptimDataLogger.disp() not implemented, to be done in subclass ' + str(type(self)))
    def plot(self):
        """plot data"""
        print('method OptimDataLogger.plot() is not implemented, to be done in subclass ' + str(type(self)))
    def data(self):
        """return logged data in a dictionary"""
        return self.dat
        
# -----------------------------------------------
class CmaesDataLogger(OptimDataLogger):
    """data logger for class Cmaes, that can store and plot data. 
    An even more useful logger would write the data to files. 
    
    """
    
    plotted = 0  
    "plot count for all instances"
    
    def __init__(self, verb_modulo=1):
        """cma is the `OOOptimizer` class instance that is to be logged, 
        `verb_modulo` controls whether logging takes place for each call 
        to the method `add()` 
        
        """
        self.modulo = verb_modulo
        self.dat = {'eval':[], 'iter':[], 'stds':[], 'D':[], 'sig':[], 'fit':[], 'xm':[]}
        self.counter = 0  # number of calls of add
    
    def add(self, cma=None, force=False):
        """append some logging data from Cmaes class instance cma, 
        if ``number_of_times_called modulo verb_modulo`` equals zero"""
        cma = self.optim if cma is None else cma
        if type(cma) is not Cmaes:
            raise TypeError('logged object must be a Cmaes class instance')
        dat = self.dat
        self.counter += 1 
        if force and self.counter == 1:
            self.counter = 0 
        if self.modulo and (len(dat['eval']) == 0 or cma.counteval != dat['eval'][-1]) and (
                self.counter < 4 or force or int(self.counter) % self.modulo == 0):
            dat['eval'].append(cma.counteval)
            dat['iter'].append(cma.counteval/cma.lam)
            dat['stds'].append([cma.C[i][i]**0.5 for i in range(len(cma.C))])
            dat['D'].append(sorted(cma.D))
            dat['sig'].append(cma.sigma)
            dat['fit'].append(cma.fitvals[0] if hasattr(cma, 'fitvals') else None) 
            dat['xm'].append([x for x in cma.xmean])
        return self
        
    def plot(self, fig_number=322):
        """plot the stored data in figure fig_number.  
    
        Dependencies: matlabplotlib/pylab. 
        
        Example
        =======
        ::
        
            >> import barecmaes2 as cma
            >> es = cma.Cmaes(3 * [0.1], 1)
            >> logger = cma.CmaesDataLogger().register(es)
            >> while not es.stop():
            >>     X = es.ask()
            >>     es.tell(X, [bc.Fcts.elli(x) for x in X])
            >>     logger.add()
            >> logger.plot() 
    
        """
        try:
            pylab.figure(fig_number)
        except: 
            print('pylab.figure() failed, nothing will be plotted')
            return None
        from pylab import text, hold, plot, ylabel, grid, semilogy, xlabel, draw, show, subplot
            
        dat = self.dat  # dictionary with entries as given in __init__
        
        try:  # a hack to get the presumable population size lambda from the data
            strpopsize = ' (popsize~' + str(dat['eval'][-2] - dat['eval'][-3]) + ')'
        except:
            strpopsize = ''
         
        # plot fit, Delta fit, sigma
        subplot(221)
        hold(False)
        if dat['fit'][0] is None:
            dat['fit'][0] = dat['fit'][1]  # should be reverted, but let's be lazy
        assert dat['fit'].count(None) == 0
        dmin = min(dat['fit'])
        i = dat['fit'].index(dmin)
        dat['fit'][i] = max(dat['fit'])
        dmin2 = min(dat['fit'])
        dat['fit'][i] = dmin 
        semilogy(dat['iter'], [d - dmin + 1e-19 if d >= dmin2 else 
                               dmin2 - dmin for d in dat['fit']], 'c', linewidth=1)
        hold(True)
        semilogy(dat['iter'], [abs(d) for d in dat['fit']], 'b')
        semilogy(dat['iter'][i], abs(dmin), 'r*')
        semilogy(dat['iter'], dat['sig'], 'g')
        ylabel('f-value, Delta-f-value, sigma')
        grid(True)

        # plot xmean
        subplot(222)
        hold(False)
        plot(dat['iter'], dat['xm'])
        hold(True)
        for i in range(len(dat['xm'][-1])):
            text(dat['iter'][0], dat['xm'][0][i], str(i))
            text(dat['iter'][-1], dat['xm'][-1][i], str(i))
        ylabel('mean solution', ha='center')
        grid(True)
        
        # plot D
        subplot(223)
        hold(False)
        semilogy(dat['iter'], dat['D'], 'm')
        xlabel('iterations' + strpopsize)
        ylabel('axes lengths')
        grid(True)

        # plot stds
        subplot(224)
        # if len(gcf().axes) > 1:
        #     sca(pylab.gcf().axes[1])
        # else:
        #     twinx()
        hold(False)
        semilogy(dat['iter'], dat['stds'])
        for i in range(len(dat['stds'][-1])):
            text(dat['iter'][-1], dat['stds'][-1][i], str(i))
        ylabel('coordinate stds disregarding sigma', ha='center')
        grid(True)
        xlabel('iterations' + strpopsize)
        
        if CmaesDataLogger.plotted == 0:
            print('    data plotted using `CmaesDataLogger.plot`, figure windows are opening, on some configurations they must be closed to unblock the console')
        sys.stdout.flush()
        draw()
        show()
        CmaesDataLogger.plotted += 1
        return None

#_____________________________________________________________________
#_______________________ Helper Functions _____________________________
#
def eye(N): 
    """return identity matrix as list of "vectors" """
    m = [N * [0] for i in range(N)]
    for i in range(N):
        m[i][i] = 1
    return m    
def dot(A, b, t=False):
    """ usual dot product of "matrix" A with "vector" b
    with t=True A is transposed, where A[i] is the i-th row of A"""
    n = len(b)
    if not t:
        m = len(A)  # number of rows, like printed by pprint 
        v = m * [0]
        for i in range(m):
            v[i] = sum(b[j] * A[i][j] for j in range(n))
    else:
        m = len(A[0])  # number of columns 
        v = m * [0]
        for i in range(m):
            v[i] = sum(b[j] * A[j][i] for j in range(n))
    return v
def dot1(a, b): 
    """scalar a times vector b"""
    return [a * c for c in b]
def plus(a, b):
    """add vectors, return a + b """
    return [a[i] + b[i] for i in range(len(a))]
def minus(a, b):
    """substract vectors, return a - b"""
    return [a[i] - b[i] for i in range(len(a))]
def argsort(a):
    """return index list to get a in order, ie a[argsort(a)[i]] == sorted(a)[i]"""
    return [a.index(val) for val in sorted(a)]

#_____________________________________________________________________
#_________________ Fitness (Objective) Functions _____________________

class Fcts(object):  # instead of a submodule
    """versatile collection of test functions"""
    
    @staticmethod  # syntax available since 2.4 
    def elli(x):
        """ellipsoid test objective function"""
        n = len(x)
        aratio = 1e3
        return sum(x[i]**2 * aratio**(2.*i/(n-1)) for i in range(n))
    @staticmethod
    def sphere(x):
        """sphere, ``sum(x**2)``, test objective function"""
        return sum(x[i]**2 for i in range(len(x)))
    @staticmethod    
    def rosenbrock(x):
        """Rosenbrock test objective function"""
        n = len(x)
        if n < 2: raise _Error('dimension must be greater one') 
        return sum(100 * (x[i]**2 - x[i+1])**2 + (x[i] - 1)**2 for i in range(n-1))

#____________________________________________________________
class _Error(Exception):
    """generic exception"""
    pass

#____________________________________________________________
#____________________________________________________________
# 
# C and B are arrays rather than matrices, because they are
# addressed via B[i][j], matrices can only be addressed via B[i,j] 

# tred2(N, B, diagD, offdiag);
# tql2(N, diagD, offdiag, B);

# Symmetric Householder reduction to tridiagonal form, translated from JAMA package.

def eig(C):
    """eigendecomposition of a symmetric matrix, much slower than 
    numpy.linalg.eigh, return the eigenvalues and an orthonormal basis 
    of the corresponding eigenvectors, ``(EVals, Basis)``, where 
    
        ``Basis[i]``
            the i-th row of ``Basis`` and columns of ``Basis``, 
        ``[Basis[j][i] for j in range(len(Basis))]``
            the i-th eigenvector with eigenvalue ``EVals[i]``
    
    """
    # class eig(object):
    #     def __call__(self, C):
    
    # Householder transformation of a symmetric matrix V into tridiagonal form. 
    # -> n             : dimension
    # -> V             : symmetric nxn-matrix
    # <- V             : orthogonal transformation matrix:
    #                    tridiag matrix == V * V_in * V^t
    # <- d             : diagonal
    # <- e[0..n-1]     : off diagonal (elements 1..n-1)

    # Symmetric tridiagonal QL algorithm, iterative 
    # Computes the eigensystem from a tridiagonal matrix in roughtly 3N^3 operations
    # -> n     : Dimension. 
    # -> d     : Diagonale of tridiagonal matrix. 
    # -> e[1..n-1] : off-diagonal, output from Householder
    # -> V     : matrix output von Householder
    # <- d     : eigenvalues
    # <- e     : garbage?
    # <- V     : basis of eigenvectors, according to d
    

    #  tred2(N, B, diagD, offdiag); B=C on input
    #  tql2(N, diagD, offdiag, B); 
    
    #  private void tred2 (int n, double V[][], double d[], double e[]) {
    def tred2 (n, V, d, e):
        #  This is derived from the Algol procedures tred2 by
        #  Bowdler, Martin, Reinsch, and Wilkinson, Handbook for
        #  Auto. Comp., Vol.ii-Linear Algebra, and the corresponding
        #  Fortran subroutine in EISPACK.

        num_opt = False  # factor 1.5 in 30-D
        if num_opt:
            import numpy as np

        for j in range(n): 
            d[j] = V[n-1][j] # d is output argument

        # Householder reduction to tridiagonal form.
    
        for i in range(n-1,0,-1):
            # Scale to avoid under/overflow.
            h = 0.0
            if not num_opt:
                scale = 0.0
                for k in range(i):
                    scale = scale + abs(d[k])
            else:
                scale = sum(abs(d[0:i]))
  
            if scale == 0.0:
                e[i] = d[i-1]
                for j in range(i):
                    d[j] = V[i-1][j]
                    V[i][j] = 0.0
                    V[j][i] = 0.0
            else:
  
                # Generate Householder vector.
                if not num_opt:
                    for k in range(i):
                        d[k] /= scale
                        h += d[k] * d[k]
                else:
                    d[:i] /= scale
                    h = np.dot(d[:i],d[:i])
   
                f = d[i-1]
                g = h**0.5
   
                if f > 0:
                    g = -g
   
                e[i] = scale * g
                h = h - f * g
                d[i-1] = f - g
                if not num_opt:
                    for j in range(i):
                        e[j] = 0.0
                else:
                    e[:i] = 0.0 
       
                # Apply similarity transformation to remaining columns.
       
                for j in range(i): 
                    f = d[j]
                    V[j][i] = f
                    g = e[j] + V[j][j] * f
                    if not num_opt:
                        for k in range(j+1, i):
                            g += V[k][j] * d[k]
                            e[k] += V[k][j] * f
                        e[j] = g
                    else:
                        e[j+1:i] += V.T[j][j+1:i] * f
                        e[j] = g + np.dot(V.T[j][j+1:i],d[j+1:i])
   
                f = 0.0
                if not num_opt:
                    for j in range(i):
                        e[j] /= h
                        f += e[j] * d[j]
                else:
                    e[:i] /= h
                    f += np.dot(e[:i],d[:i]) 
   
                hh = f / (h + h)
                if not num_opt:
                    for j in range(i): 
                        e[j] -= hh * d[j]
                else:
                    e[:i] -= hh * d[:i]
                    
                for j in range(i): 
                    f = d[j]
                    g = e[j]
                    if not num_opt:
                        for k in range(j, i): 
                            V[k][j] -= (f * e[k] + g * d[k])
                    else:
                        V.T[j][j:i] -= (f * e[j:i] + g * d[j:i])
                        
                    d[j] = V[i-1][j]
                    V[i][j] = 0.0
  
            d[i] = h
        # end for i--
    
        # Accumulate transformations.

        for i in range(n-1): 
            V[n-1][i] = V[i][i]
            V[i][i] = 1.0
            h = d[i+1]
            if h != 0.0:
                if not num_opt:
                    for k in range(i+1): 
                        d[k] = V[k][i+1] / h
                else:
                    d[:i+1] = V.T[i+1][:i+1] / h
                   
                for j in range(i+1): 
                    if not num_opt:
                        g = 0.0
                        for k in range(i+1): 
                            g += V[k][i+1] * V[k][j]
                        for k in range(i+1): 
                            V[k][j] -= g * d[k]
                    else:
                        g = np.dot(V.T[i+1][0:i+1], V.T[j][0:i+1])
                        V.T[j][:i+1] -= g * d[:i+1]
 
            if not num_opt:
                for k in range(i+1): 
                    V[k][i+1] = 0.0
            else:
                V.T[i+1][:i+1] = 0.0
               

        if not num_opt:
            for j in range(n): 
                d[j] = V[n-1][j]
                V[n-1][j] = 0.0
        else:
            d[:n] = V[n-1][:n]
            V[n-1][:n] = 0.0

        V[n-1][n-1] = 1.0
        e[0] = 0.0


    # Symmetric tridiagonal QL algorithm, taken from JAMA package.
    # private void tql2 (int n, double d[], double e[], double V[][]) {
    # needs roughly 3N^3 operations
    def tql2 (n, d, e, V):
        #  This is derived from the Algol procedures tql2, by
        #  Bowdler, Martin, Reinsch, and Wilkinson, Handbook for
        #  Auto. Comp., Vol.ii-Linear Algebra, and the corresponding
        #  Fortran subroutine in EISPACK.
    
        num_opt = False  # using vectors from numpy make it faster

        if not num_opt:
            for i in range(1,n): # (int i = 1; i < n; i++): 
                e[i-1] = e[i]
        else:
            e[0:n-1] = e[1:n]
        e[n-1] = 0.0
    
        f = 0.0
        tst1 = 0.0
        eps = 2.0**-52.0
        for l in range(n): # (int l = 0; l < n; l++) {

            # Find small subdiagonal element
     
            tst1 = max(tst1, abs(d[l]) + abs(e[l]))
            m = l
            while m < n: 
                if abs(e[m]) <= eps*tst1:
                    break
                m += 1
 
            # If m == l, d[l] is an eigenvalue,
            # otherwise, iterate.
     
            if m > l:
                iiter = 0
                while 1: # do {
                    iiter += 1  # (Could check iteration count here.)
     
                    # Compute implicit shift
     
                    g = d[l]
                    p = (d[l+1] - g) / (2.0 * e[l])
                    r = (p**2 + 1)**0.5  # hypot(p,1.0) 
                    if p < 0:
                        r = -r
 
                    d[l] = e[l] / (p + r)
                    d[l+1] = e[l] * (p + r)
                    dl1 = d[l+1]
                    h = g - d[l]
                    if not num_opt: 
                        for i in range(l+2, n):
                            d[i] -= h
                    else:
                        d[l+2:n] -= h
 
                    f = f + h
     
                    # Implicit QL transformation.
     
                    p = d[m]
                    c = 1.0
                    c2 = c
                    c3 = c
                    el1 = e[l+1]
                    s = 0.0
                    s2 = 0.0
 
                    # hh = V.T[0].copy()  # only with num_opt
                    for i in range(m-1, l-1, -1): # (int i = m-1; i >= l; i--) {
                        c3 = c2
                        c2 = c
                        s2 = s
                        g = c * e[i]
                        h = c * p
                        r = (p**2 + e[i]**2)**0.5  # hypot(p,e[i])
                        e[i+1] = s * r
                        s = e[i] / r
                        c = p / r
                        p = c * d[i] - s * g
                        d[i+1] = h + s * (c * g + s * d[i])
     
                        # Accumulate transformation.
     
                        if not num_opt: # overall factor 3 in 30-D
                            for k in range(n): # (int k = 0; k < n; k++) {
                                h = V[k][i+1]
                                V[k][i+1] = s * V[k][i] + c * h
                                V[k][i] = c * V[k][i] - s * h
                        else: # about 20% faster in 10-D
                            hh = V.T[i+1].copy()
                            # hh[:] = V.T[i+1][:]
                            V.T[i+1] = s * V.T[i] + c * hh
                            V.T[i] = c * V.T[i] - s * hh
                            # V.T[i] *= c
                            # V.T[i] -= s * hh
 
                    p = -s * s2 * c3 * el1 * e[l] / dl1
                    e[l] = s * p
                    d[l] = c * p
     
                    # Check for convergence.
                    if abs(e[l]) <= eps*tst1:
                        break
                # } while (Math.abs(e[l]) > eps*tst1);
 
            d[l] = d[l] + f
            e[l] = 0.0
       

        # Sort eigenvalues and corresponding vectors.
        if 11 < 3:
            for i in range(n-1): # (int i = 0; i < n-1; i++) {
                k = i
                p = d[i]
                for j in range(i+1, n): # (int j = i+1; j < n; j++) {
                    if d[j] < p: # NH find smallest k>i
                        k = j
                        p = d[j]

                if k != i: 
                    d[k] = d[i] # swap k and i 
                    d[i] = p   
                    for j in range(n): # (int j = 0; j < n; j++) {
                        p = V[j][i]
                        V[j][i] = V[j][k]
                        V[j][k] = p
    # tql2
    N = len(C[0])
    V = [C[i][:] for i in range(N)]
    d = N * [0]
    e = N * [0]
    tred2(N, V, d, e)
    tql2(N, d, e, V)
    return (d, V)
 
def _test():
    """
    >>> import barecmaes2 as cma
    >>> import random
    >>> random.seed(5)
    >>> x = cma.fmin(cma.Fcts.rosenbrock, 4 * [0.5], 0.5, verb_plot=0)
    evals: ax-ratio max(std)   f-value
        8:     1.0  4.3e-01  8.17705253283
       16:     1.1  4.2e-01  66.2003009423
      160:     3.1  1.7e-01  2.89654538036
      320:     6.7  7.0e-02  1.18902793656
      480:    10.8  5.2e-02  0.433584950845
      640:    15.0  4.1e-02  0.170056758523
      800:    19.1  3.8e-02  0.0423501042891
      960:    35.3  2.6e-02  0.00228179626711
     1120:    49.8  8.8e-03  7.07307150746e-05
     1280:    44.1  9.1e-04  8.25068128793e-07
     1440:    49.5  6.5e-05  4.14827079218e-09
    evals: ax-ratio max(std)   f-value
     1600:    46.1  4.7e-06  1.14801950628e-11
     1736:    59.2  5.4e-07  1.26488753189e-13
    termination by {'tolfun': 1e-12}
    best f-value = 4.93281796387e-14
    solution = [0.9999999878867273, 0.9999999602211, 0.9999999323618144, 0.9999998579200512]

  """
  
    import doctest
    print('launching doctest')
    doctest.testmod(report=True)  # module test
    print('done (ideally no line between launching and done was printed, python 3.x shows slight deviations)')

#_____________________________________________________________________
#_____________________________________________________________________
#
if __name__ == "__main__":

    _test()

    # fmin(Fcts.rosenbrock, 10 * [0.5], 0.5)
