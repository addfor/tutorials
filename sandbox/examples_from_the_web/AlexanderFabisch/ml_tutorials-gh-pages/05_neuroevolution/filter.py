import numpy, pylab

class ABF(object):
    """Alpha-beta filter."""
    def __init__(self, g, delta):
        r = (4+g-numpy.sqrt(8*g+g**2))/4
        self.a = 1-r**2
        self.b = 2*(1-r)**2
        self.delta = delta
        self.s = None
        self.sd = None
    def step(self, s):
        if self.s == None:
            self.s = s
            self.sd = numpy.zeros_like(s)
        se = self.s + self.delta * self.sd
        sde = self.sd
        r = s - se
        self.s = se + self.a * r
        self.sd = sde + self.b/self.delta * r
        return self.s, self.sd

if __name__ == "__main__":
    numpy.random.seed(0)

    gamma = 0.01

    f = ABF(gamma, 1.0)
    steps = 100
    X = numpy.linspace(0, numpy.pi*4, steps)
    S = numpy.sin(X)
    SD = numpy.cos(X)
    Sn = S + numpy.random.randn(*S.shape)*0.1
    SE = []
    SDE = []
    for s in range(steps):
        se, sd = f.step(Sn[s])
        SE.append(se)
        SDE.append(sd)

    pylab.plot(SE)
    pylab.plot(Sn)
    pylab.plot(S)
    #pylab.plot(SD)
    #pylab.plot(SDE)
    pylab.show()
