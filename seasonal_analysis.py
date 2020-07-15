from datetime import datetime, timedelta
import pandas as pd
# from tensorflow import keras
import statsmodels.api as sm#from statsmodels.api.tsa.statespace import SARIMAX
import statsmodels.tsa as tsa
import sys

from mlogging import log
from ticker_data import Ticker


class Analyst():
  datum = {}

  def __init__(self, components, end):
    log('INFO', 'Getting seasonal time series')
    for i, component in enumerate(components):
      ticker = Ticker(component['symbol'])
      log('INFO', 'seasonal time series for '+component['symbol']+' '+str(i+1)+'/'+str(len(components)))
      ticker_datum = ticker.get_daily_n_year_data(n=4, end=end)
      X = list(map(lambda x: x['datetime'], ticker_datum))
      Y = list(map(lambda x: x['close'], ticker_datum))
      self.datum[(component['symbol'], component['name'])] = {
        'SARIMA':self.sarimax_predictions(X, Y),
        'HoltWintersExp':self.holtwinters_predictions(X, Y),
      }

  def sarimax_predictions(self, X, Y, extrapolated_days=15):
    df = pd.DataFrame({'index':X, 'Y':Y})
    sarimax_model = sm.tsa.statespace.SARIMAX(df['Y'], trend='n', order=(0,1,0), seasonal_order=(1,1,1,12)).fit(disp=False)
    predictions = sarimax_model.predict(start=len(X), end=len(X)+extrapolated_days, exog=X)
    base_date = X[-1]
    output = {}
    for prediction in predictions:
      base_date = base_date+timedelta(days=1)
      while base_date.weekday() in [5,6]: #skip Saturday and Sunday
        base_date = base_date+timedelta(days=1)
      output[str(datetime.timestamp(base_date))] = prediction
    return output

  def holtwinters_predictions(self, X, Y, extrapolated_days=15):
    #make the Y values positive for multiplicative models
    Y = map(lambda y: sys.float_info.min if y is None or y<=0 else y, Y)
    df = pd.DataFrame({'index':X, 'Y':Y})
    try:
      holtwinters_model = tsa.holtwinters.ExponentialSmoothing(df['Y'], seasonal='mul', seasonal_periods=12).fit()
    except:
      holtwinters_model = tsa.holtwinters.ExponentialSmoothing(df['Y'], seasonal='add', seasonal_periods=12).fit()
    predictions = holtwinters_model.predict(start=len(X), end=len(X)+extrapolated_days)
    base_date = X[-1]
    output = {}
    for prediction in predictions:
      base_date = base_date+timedelta(days=1)
      while base_date.weekday() in [5,6]: #skip Saturday and Sunday
        base_date = base_date+timedelta(days=1)
      output[str(datetime.timestamp(base_date))] = prediction
    return output

    # def lstmnn_predictions(self, X, Y, extrapolated_days=15):
    #   lstmnn = keras.models.Sequential()
      

  def get(self):
    return self.datum


if __name__=='__main__':
  # from datetime import datetime
  # import pandas as pd
  # from ticker_data import Ticker
  # import statsmodels.api as sm#from statsmodels.api.tsa.statespace import SARIMAX
  # end = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
  # ticker = Ticker('Z74.SI')
  # ticker_datum = ticker.get_daily_n_year_data(n=4, end=end)
  # X = list(map(lambda x: x['datetime'], ticker_datum))
  # Y = list(map(lambda x: x['close'], ticker_datum))
  # df = pd.DataFrame({'index':X, 'Y':Y})
  #sarimax_model = sm.tsa.statespace.SARIMAX(df['Y'], trend='n', order=(0,1,0), seasonal_order=(1,1,1,12)).fit(disp=False)
  #predictions = sarimax_model.predict(start=len(X), end=len(X)+15, exog=X)
##############
  from datetime import datetime
  datum = Analyst([{'name':'Oversea-Chinese Banking Corporation Limited', 'symbol':'O39.SI'}], datetime(2020, 4, 4)).get()
  import pprint
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(datum)
