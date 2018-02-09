import pandas as pd
from pandas_datareader.data import DataReader
from pandas_datareader._utils import RemoteDataError
import numpy as np
from .tom import TomTom
import os
import shutil


def p01_d2csv(tomtom):
    d = {'a' : pd.Series(['one','one','two','three','two']),
     'b' : pd.Series(['x','y','y','x','y']),
     'c' : pd.Series(np.random.randn(5))}
    d2 = pd.DataFrame(d)
    d2.to_csv(tomtom.get_tmp_name('p01_d2.csv'))

def p01_d3csv(tomtom):
    comuni = pd.read_csv(tomtom.get_example_name('tabella_comuni_italiani.txt'),
                         sep=';', header=0)
    # d3 = pd.DataFrame(np.random.randn(1000, 100), columns=comuni['Comune'].ix[0:199])
    comuni.to_csv(tomtom.get_tmp_name('p01_d3.csv'), index=False)

def p01_d4csv(tomtom):
    idx = [('Fra', 'one', 'x'),
           ('Fra', 'two', 'y'),
           ('Fra', 'two', 'z'),
           ('Ger', 'one', 'x'),
           ('Jap', 'one', 'x'),
           ('Jap', 'two', 'x'),
           ('USA', 'one', 'y'),
           ('USA', 'one', 'z')]
    index = pd.MultiIndex.from_tuples(idx, names=['Country', 'Number', 'Dir'])
    d4 = pd.DataFrame(np.random.randn(8,3), index=index)
    d4.to_csv(tomtom.get_tmp_name('p01_d4.csv'))

def p01_prices(tomtom):
    try:
        symbols = ['AAPL', 'JNJ', 'XOM', 'GOOG']
        data = dict([(sym, DataReader(sym, 'yahoo')['Close']) for sym in symbols])
        df = pd.DataFrame.from_dict(data)
        df.ix[-7:-1].to_csv(tomtom.get_tmp_name('p01_prices.txt'))
    except RemoteDataError:
        print('Error while reading data, revert to stored file in example_data')
        shutil.copy('example_data/p01_prices.txt', 'temp')

def p01_volumes(tomtom):
    try:
        symbols = ['AAPL', 'JNJ', 'XOM']
        data = dict([(sym, DataReader(sym, 'yahoo')['Volume']) for sym in symbols])
        df = pd.DataFrame.from_dict(data)
        df.ix[-7:-3].to_csv(tomtom.get_tmp_name('p01_volumes.txt'))
    except RemoteDataError:
        print('Error while reading data, revert to stored file in example_data')
        shutil.copy('example_data/p01_volumes.txt', 'temp')
    
def p03_DAX(tomtom):
    try:
        DAX = DataReader('^GDAXI','yahoo',start = '01/01/2000')
        DAX.to_csv(tomtom.get_tmp_name('p03_DAX.csv'))
    except RemoteDataError:
        print('Error while reading data, revert to stored file in example_data')
        shutil.copy('example_data/p03_DAX.csv', 'temp')

def p03_AAPL(tomtom):
    try:
        DAX = DataReader('AAPL','yahoo',start = '01/01/2000')
        DAX.to_csv(tomtom.get_tmp_name('p03_AAPL.csv'))
    except RemoteDataError:
        print('Error while reading data, revert to stored file in example_data')
        shutil.copy('example_data/p03_AAPL.csv', 'temp')

def p06_d3csv(tomtom):
    d2 = pd.DataFrame({'City' : ['New York', ' frisco', 'houston', ' taft', 'venice'],
                'State' : [' NY ', 'CA', '  tx ', '   OK', '  IL'],
                'Name' : ['Roy', 'Johnn', 'Jim', 'Paul', 'Ross'],
                'Revenues' : ['1250', '840', '349', '1100', '900']})
    d2.to_csv(tomtom.get_tmp_name('p06_d2.txt'))

def p06_d2csv(tomtom):
    d3 = pd.DataFrame({'Quantity' : ['1-one', '1-one', '2-two', '3-three'] * 6,
                'Axis' : ['X', 'Y', 'Z'] * 8,
                'Type' : ['foo', 'foo', 'foo', 'bar', 'bar', 'bar'] * 4,
                'N1' : np.random.randn(24),
                'N2' : np.random.randn(24)})
    d3.to_csv(tomtom.get_tmp_name('p06_d3.txt'))


def p07_d1csv(tomtom):
    d1 = pd.DataFrame({'State' : ['NE','KY','CO','CO','KY','KY','CO','NE','CO'],
                    'City' : ['Page','Stone','Rye','Rye','Dema','Keavy','Rye',
                              'Cairo', 'Dumont'],
                    'Views' : [10, 9, 3, 7, 4, 2, 1, 8, 12],
                    'Likes' : [4, 3, 0, 2, 1, 1, 0, 3, 7]})
    d1.to_csv(tomtom.get_tmp_name('p07_d1.txt'))

def p07_d2csv(tomtom):
    import random; random.seed(0)
    import string
    N = 1000
    def rands(n):
        choices = string.ascii_uppercase
        return ''.join([random.choice(choices) for _ in range(n)])

    tickers = np.array([rands(5) for _ in range(N)])

    # Create a DataFrame containing 3 columns representing
    # hypothetical, but random portfolios for a subset of tickers:
    d2 = pd.DataFrame({'Momentum' : np.random.randn(500) / 200 + 0.03,
                   'Value' : np.random.randn(500) / 200 + 0.08,
                   'ShortInterest' : np.random.randn(500) / 200 - 0.02},
                   index=tickers.take(np.random.permutation(N)[:500]))

    # Next, let's create a random industry classification for the tickers.
    ind_names = np.array(['FINANCIAL', 'TECH'])
    sampler = np.random.randint(0, len(ind_names), N)
    industries = pd.Series(ind_names.take(sampler), index=tickers, name='industry')
    d2['Industry'] = industries

    d2.to_csv(tomtom.get_tmp_name('p07_d2.csv'))

def p07_portfolioh5(tomtom):
    import random; random.seed(0)
    import string
    N = 1000
    def rands(n):
        choices = string.ascii_uppercase
        return ''.join([random.choice(choices) for _ in range(n)])

    tickers = np.array([rands(5) for _ in range(N)])
    fac1, fac2, fac3 = np.random.rand(3, 1000)
    ticker_subset = tickers.take(np.random.permutation(N)[:1000])

    # portfolio = weighted sum of factors plus noise
    portfolio = pd.Series(0.7 * fac1 - 1.2 * fac2 + 0.3 * fac3 + np.random.rand(1000),
                      index=ticker_subset)
    factors = pd.DataFrame({'f1': fac1, 'f2': fac2, 'f3': fac3},
                        index=ticker_subset)

    h5file = pd.HDFStore(tomtom.get_tmp_name('p07_portfolio.h5'))
    h5file['factors'] = factors
    h5file['portfolio'] = portfolio
    h5file.close()

def baby_names(tomtom):
    import zipfile
    path = tomtom.get_example_name('babynames.zip')
    opath = tomtom.get_tmp_name("")
    z = zipfile.ZipFile(path, "r")
    z.extractall(path=opath)
    
generators = {
    'baby_names/': baby_names,
    'p07_portfolio.h5': p07_portfolioh5,
    'p07_d2.csv': p07_d2csv,
    'p07_d1.txt': p07_d1csv,
    'p06_d3.txt': p06_d3csv,
    'p06_d2.txt': p06_d2csv,
    'p03_DAX.csv': p03_DAX,
    'p03_AAPL.csv': p03_AAPL,
    'p01_prices.txt': p01_prices,
    'p01_d2.csv': p01_d2csv,
    'p01_d3.csv': p01_d3csv,
    'p01_d4.csv': p01_d4csv,
    'p01_volumes.txt': p01_volumes,
    }

def generate_all():
    tomtom = TomTom()
    for filename, gen in generators.items():
        path = tomtom.get_tmp_name(filename)
        if not os.path.exists(path):
            print("Generating {}...".format(filename))
            gen(tomtom)
        else:
            print("Skipped {} (already existing)".format(filename))

if __name__ == '__main__':
    generate_all()            
