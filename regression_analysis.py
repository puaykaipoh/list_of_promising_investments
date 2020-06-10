from datetime import datetime
import sys

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from time import mktime

from mlogging import log
from ticker_data import Ticker


class Analyst():
  datum = []

  def __init__(self, components, end):
    self.monthly_datum = {}
    log('INFO', 'Getting regression time series')
    for i, component in enumerate(components):
      ticker = Ticker(component['symbol'])
      log('INFO', 'regression time series for '+component['symbol']+' '+str(i+1)+'/'+str(len(components)))
      ticker_datum = ticker.get_hourly_month_data(end)
      segments = []
      overall_trend = 0
      X = np.array(list(map(lambda d: 
          mktime(d['datetime'].timetuple())
        ,ticker_datum)))
      Y = np.array(list(map(lambda d: 
          d['close']
        ,ticker_datum)))
      #start remove all the None
      prev = X[0] #
      for i in range(1, len(X)):
        if X[i] == None:
          X[i] = prev
        else:
          prev = X[i]
      prev = Y[0]
      for i in range(1, len(Y)):
        if Y[i] == None:
          Y[i] = prev
        else:
          prev = Y[i]
      #end remove ll the None
      for x_start, x_end, y_start, y_end, coef, intercept, error in self._segmented_least_squares(X, Y,
        0.0078125 # TODO this should be configurable; 0.25=2 segments; 0.0078125 = 3 segments for 4 jun 2020 singtel
      ):
        segments.append({
          'x_start':datetime.strftime(datetime.fromtimestamp(x_start), '%Y-%m-%d %H:%M'),
          'x_end':datetime.strftime(datetime.fromtimestamp(x_end), '%Y-%m-%d %H:%M'),
          'y_start':y_start,
          'y_end':y_end,
          'coef':coef[0],
          'intercept':intercept,
          'percentage_slope':coef[0]/abs(intercept),
          'error':error
        })
        #longer the trend the stronger, the later the stronger, the smaller the error the stronger the trend, percentage slope gives the sign and strength of trend
        overall_trend += ((x_end - x_start) * x_end * (1/error) * (coef[0]/abs(intercept)))/1000000
      self.monthly_datum[component['symbol']] = {"segments":segments, 'overall_trend':overall_trend}
    self.datum = self.monthly_datum

  def get(self):
    return self.datum

  def _segmented_least_squares(self, X, Y, Cfactor):
    #https://github.com/solohikertoo/segmented-least-squares/blob/master/segleastsquares.py
    #datum = np.array([[0, 0], [1, 1], [2, 2]])
    try:
      X = np.nan_to_num(X)
      Y = np.nan_to_num(Y)
      ##############TODO debugging
      # if np.isnan(X).any() or np.isinf(X).any():
      #   print('_segmented_least_squares X', X)
      # if np.isnan(Y).any() or np.isinf(Y).any():
      #   print('_segmented_least_squares Y', Y)
      #############TODO debugging
      n = X.size
      preresult = self._precompute(n, X, Y)
      C = self._penalty(Y, Cfactor)
      opt = self._findopt(n, preresult, C)
      yfit = self._construct_fit(n, X, Y, preresult, opt)
      return yfit
    except:
      import traceback
      traceback.print_exc()
      print('***************')
      print('_segmented_least_squares X', X)
      print('_segmented_least_squares Y', Y)


  def _least_squares(self, X, Y):
    try:
      X_p = np.array(list(map(lambda x: [x], X)))
      X_p = np.nan_to_num(X_p)
      Y = np.nan_to_num(Y)
      ##################################
      # if np.isnan(X_p).any() or np.isinf(X_p).any():
      #   print('_least_squares X_p', X_p)
      # if np.isnan(Y).any() or np.isinf(Y).any():
      #   print('_least_squares Y', Y)
      ##################################
      regression_model = LinearRegression().fit(X_p, Y)
      pred_Y = regression_model.predict(X_p)
      pred_Y = np.nan_to_num(pred_Y)
      return (regression_model.coef_, regression_model.intercept_, mean_squared_error(Y, pred_Y))
    except:
      import traceback
      traceback.print_exc()
      print('!!!!!!!!!!!!!!!!!!!!')
      print('_least_squares X', X)
      print('_least_squares Y', Y)


  def _precompute(self, n, X, Y):
    result = []
    for j in range(n):
      jres = []
      for i in range(0, j+1):
        jres = jres + [self._least_squares(X[i:j+1], Y[i:j+1])]
      result = result + [jres]
    return result

  def _findopt(self, n, preresult, C):
    optresult = []
    for j in range(0, n):
      beste = sys.float_info.max
      besti = -1
      jpre = preresult[j] # list of tuples (a, b, e) for i=0, ..., j
      for i in range(0, j+1):
        # get the error assuming using opt to 
        # with penalty per segment, C
        if (i > 0):
          e = jpre[i][2] + optresult[i-1][0] + C
        else:
          e = jpre[i][2] + C
        # find i with the smallest error
        if (e < beste):
          beste = e
          besti = i
      #create opt entry for k, consisting of min error and list of (i, j)
      #this is a list of (i, j) segments for this j, consisting of 
      # the current best (i, j) appended to list from opt[besti-1]
      if (besti > 0):
        optresult = optresult + [[beste, optresult[besti-1][1] + [(besti, j)]]]
      else:
        optresult = optresult + [[beste, [(besti, j)]]]
    return optresult[n-1]

  def _construct_fit(self, n, X, Y, preresult, opt):
    print('opt', opt)
    segments = [] # (start_timestamp, end_timestamp, start_price, end_price, coefficient, intercept, error)
    optintervals = opt[1] #list of tuples (opt has errorand list of tuples)
    #for each segment
    for interval in optintervals:
      i = interval[0]
      j = interval[1]
      result = preresult[j][i]
      #(X_start, X_end, Y_start, Y_end, a, b, error); y=ax+b
      segments.append((X[i], X[j], Y[i], Y[j], result[0], result[1], result[2]))
    return segments

  def _penalty(self, Y, C):
    return Y.var() * C

if __name__=='__main__':
  from datetime import datetime
  datum = Analyst([{'symbol':'C31.SI'}], datetime(2020, 4, 4)).get()
  import pprint
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(datum)