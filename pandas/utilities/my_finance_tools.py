from datetime import datetime
import matplotlib.finance as fin
import pandas as pd
from pandas import Index, DataFrame
from pandas.core.datetools import BMonthEnd

# MY FINANCE TOOLS -------------------------------------------------------------
''' Created by: Addfor s.r.l.
    This module provides few example finance and utility functions
    '''

def csv_preview(filename, lines_to_print=5):
    '''
    TODO - Add a control to define how many columns to print:
              start_column = 0
              end_column = 79
    '''
    with open(filename) as fid:
        for _ in range(lines_to_print):
            line = fid.readline()
            print line,

def side_by_side(*objs, **kwds):
    space = kwds.get('space', 4)
    reprs = [repr(obj).split('\n') for obj in objs]
    print '-'*40
    print pd.core.common.adjoin(space, *reprs)
    print '-'*40

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