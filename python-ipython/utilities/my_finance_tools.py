from datetime import datetime
import matplotlib.finance as fin
from pandas import Index, DataFrame
from pandas.core.datetools import BMonthEnd

# MY FINANCE TOOLS -------------------------------------------------------------
''' Created by: Addfor S.p.A.
    This module provides few example finance functions
    '''

def getQuotes(symbol, start, end):
    '''getQuotes documentation'''
    quotes = fin.quotes_historical_yahoo(symbol, start, end)
    dates, opn, close, high, low, volume = zip(*quotes)
    data = {'open': opn, 'close': close, 'high' : high,
            'low' : low, 'volume': volume}

    dates = Index([datetime.fromordinal(int(d)) for d in dates])
    return DataFrame(data, index=dates)
    

def toMonthly(frame, how):
    '''toMonthly documentation'''
    offset = BMonthEnd()
    return frame.groupby(offset.rollforward).aggregate(how)
