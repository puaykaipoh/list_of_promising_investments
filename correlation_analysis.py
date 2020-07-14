from statistics import mean

from mlogging import log
from ticker_data import Ticker


class Analyst():
  datum = []

  def __init__(self, components, end):
    self.yearly_datum = {}
    log('INFO', 'Getting correlation time series')
    for i, component in enumerate(components):
      ticker = Ticker(component['symbol'])
      log('INFO', 'correlation time series for '+component['symbol']+' '+str(i+1)+'/'+str(len(components)))
      self.yearly_datum[component['symbol']] = list(map(lambda d: {
        'datetime':d['datetime'], 
        'value':d['close']}, ticker.get_daily_year_data(end)))
      if len(self.yearly_datum[component['symbol']]) == 0:
        raise Exception('correlation analyst cannot get time series for '+component['symbol'])
    log('INFO', 'Computing correlation')
    for i, x_component in enumerate(components):
      row = [x_component['name'], x_component['symbol'], {}]
      for j, y_component in enumerate(components):
        if i == j:
          break
        X, Y = self._line_up_raw_datum(
          self.yearly_datum[x_component['symbol']],
          self.yearly_datum[y_component['symbol']])
        row[2][(y_component['name'], y_component['symbol'])] = self._linear_correlation(X, Y)
      self.datum.append(row)
    self.datum.reverse()
    self.datum.pop()

  def _line_up_raw_datum(self, datum0, datum1):#datum is list of dictionary with keys: [datetime, value]
    matching_datetime = set(map(lambda d:d['datetime'], datum0)).intersection(set(map(lambda d:d['datetime'], datum1)))
    datum0 = dict(map(lambda d:(d['datetime'], d['value']), datum0))
    datum1 = dict(map(lambda d:(d['datetime'], d['value']), datum1))
    X = []
    Y = []
    for dt in list(matching_datetime):
      if dt in datum0 and dt in datum1:
        X.append(datum0[dt])
        Y.append(datum1[dt])
    return X, Y


  def _n_moment(self, datum, n=1):
    datum = map(lambda x: 0 if x is None else x, datum)
    if n == 1:
      return mean(datum)
    return mean(map(lambda x: x**n, datum))

  def _linear_correlation(self, X, Y):
    E = {
      'X':self._n_moment(X),
      'X2':self._n_moment(X,n=2),
      'Y':self._n_moment(Y),
      'Y2':self._n_moment(Y, n=2),
      'XY':mean(map(lambda d: d[0]*d[1], zip(X, Y)))
    }
    return (E['XY'] - E['X']*E['Y'])/(((E['X2'] - (E['X']*E['X']))*(E['Y2'] - (E['Y']*E['Y'])))**0.5)


  def get(self):
    return self.datum

if __name__=='__main__':
  from sti_components import STIComponents
  from datetime import datetime, timedelta
  components = STIComponents().get()
  datum = Analyst(components, datetime.utcnow() ).get()
  from formater import Formater
  content = Formater()._correlation(datum)
  from filer import Filer
  Filer().file(content)
