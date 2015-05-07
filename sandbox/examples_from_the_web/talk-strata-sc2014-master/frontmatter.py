from IPython.display import display, Image, HTML

class _ellisonbg(object):


    def _repr_html_(self):
        s = '<h3><a href="http://www.brianegranger.com" target="_blank">Brian E. Granger</a></h3>'
        s += '<h3><a href="http://calpoly.edu" target="_blank">Cal Poly</a> <a href="http://physics.calpoly.edu/" target="_blank">Physics Department</a></h3>'
        s += '<h3><a href="http://ipython.org" target="_blank">IPython Project</a></h3>'
        s += '<h3><a href="https://twitter.com/ellisonbg" target="_blank">@ellisonbg</a></h3>'
        return s
    
    def __repr__(self):
        s = "Brian E. Granger\n"
        s += "Cal Poly Physics Department\n"
        s += "IPython Project"
        s += "@ellisonbg"
        return s

_bio_text = """Brian Granger is an Assistant Professor of Physics at Cal Poly State University in San
Luis Obispo, CA. He has a background in theoretical atomic, molecular and optical physics,
with a Ph.D from the University of Colorado. His current research interests include
quantum computing, parallel and distributed computing and interactive computing
environments for scientific and technical computing. He is a core developer of the IPython
project and is an active contributor to a number of other open source projects focused on
scientific computing in Python. He is @ellisonbg on Twitter and GitHub."""

class _bio(object):
    
    def _repr_html_(self):
        return _bio_text
    
    def __repr__(self):
        return _bio_text

def whoami():
    display(_ellisonbg())

def bio():
    display(_bio())

def logos():
    display(Image('images/calpoly_logo.png'))
    display(Image('images/ipython_logo.png'))


    