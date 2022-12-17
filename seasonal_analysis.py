from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from tensorflow import keras
from statistics import mean
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
      try:
        ticker = Ticker(component['symbol'])
        log('INFO', 'seasonal time series for '+component['symbol']+' '+str(i+1)+'/'+str(len(components)))
        ticker_datum = ticker.get_daily_n_year_data(n=4, end=end)
        X = list(map(lambda x: x['datetime'], ticker_datum))
        Y = list(map(lambda x: x['close'], ticker_datum))
        self.datum[(component['symbol'], component['name'])] = {
          'SARIMA':self.sarimax_predictions(X, Y),
          'HoltWintersExp':self.holtwinters_predictions(X, Y),
          'LSTMNN':self.lstmnn_predictions(X,Y),
        }
      except:
        import traceback
        log('ERROR', 'seasonal_analysis %s: %s' % (component, traceback.format_exc()))

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

  def lstmnn_predictions(self, X, Y, extrapolated_days=15):
    #normalize Y
    average = mean(Y)
    largest_diff_from_zero = max(map(lambda y: abs(y-average), Y))
    Y = list(map(lambda y: (y-average)/largest_diff_from_zero, Y))
    time_lag = int(0.08 * len(X)) # take 8% of length
    #START preparing the data
    training_datum = []
    label_datum = []
    for i in range(0, len(X)-time_lag-extrapolated_days):
      training_data = []
      for j in range(i, i+time_lag):
        training_data.append(X[j].year)
        training_data.append(X[j].month)
        training_data.append(X[j].day)
        training_data.append(X[j].weekday())
        training_data.append(Y[j])
      training_datum.append(training_data)
      label_datum.append(Y[i+time_lag:i+time_lag+extrapolated_days])
    #END preparing the data
    lstmnn = keras.models.Sequential([
        #keras.layers.BatchNormalization(),
        keras.layers.Conv1D(filters=extrapolated_days, kernel_size=time_lag, padding="same", activation="relu"),# input_shape=(len(training_datum[0]), len(training_datum[1]))),
        keras.layers.LSTM(int(0.32*len(X)), return_sequences=True),
        keras.layers.LSTM(int(0.32*len(X)), return_sequences=True),
        keras.layers.Dense(extrapolated_days, activation='relu'),
        keras.layers.Dense(extrapolated_days, activation='linear'),
    ])
    optimizer = keras.optimizers.SGD(learning_rate=0.0001, momentum=0.9)
    lstmnn.compile(loss=keras.losses.binary_crossentropy, optimizer=optimizer, metrics=["mae"])
    #TODO need to normalize
    #add dummy dimension for Conv1D
    lstmnn.fit(np.array([training_datum]), np.array([label_datum]), verbose=1, epochs=64, batch_size=len(training_datum))
    results = lstmnn.predict(np.array([training_datum[-2:-1]]))[-1].tolist()[-1]#lstmnn.predict(np.array([training_datum[-1*(extrapolated_days+1):-1]]))
    #unnormalize predictions
    predictions = list(map(lambda y: (y*largest_diff_from_zero)+average,results))
    base_date = X[-1]
    output = {}
    for prediction in predictions:
        base_date = base_date+timedelta(days=1)
        while base_date.weekday() in [5,6]: #skip Saturday and Sunday
            base_date = base_date+timedelta(days=1)
        output[str(datetime.timestamp(base_date))] = prediction
    return output

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
    from tensorflow import keras
    import numpy as np
    from ticker_data import Ticker
    ticker = Ticker('Z74.SI')
    end = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ticker_datum = ticker.get_daily_n_year_data(n=4, end=end)
    ticker_datum.sort(key=lambda x:x['datetime'])
    X = list(map(lambda x: x['datetime'], ticker_datum))
    Y = list(map(lambda x: x['close'], ticker_datum))
    extrapolated_days=15##############################################
    #normalize Y
    average = mean(Y)
    largest_diff_from_zero = max(map(lambda y: abs(y-average), Y))
    Y = list(map(lambda y: (y-average)/largest_diff_from_zero, Y))
    time_lag = int(0.08 * len(X)) # take 8% of length
    #START preparing the data
    training_datum = []
    label_datum = []
    for i in range(0, len(X)-time_lag-extrapolated_days):
      training_data = []
      for j in range(i, i+time_lag):
        training_data.append(X[j].year)
        training_data.append(X[j].month)
        training_data.append(X[j].day)
        training_data.append(X[j].weekday())
        training_data.append(Y[j])
      training_datum.append(training_data)
      label_datum.append(Y[i+time_lag:i+time_lag+extrapolated_days])
    #END preparing the data
    lstmnn = keras.models.Sequential([
        #keras.layers.BatchNormalization(),
        keras.layers.Conv1D(filters=extrapolated_days, kernel_size=time_lag, padding="same", activation="relu"),# input_shape=(len(training_datum[0]), len(training_datum[1]))),
        keras.layers.LSTM(int(0.32*len(X)), return_sequences=True),
        keras.layers.LSTM(int(0.32*len(X)), return_sequences=True),
        keras.layers.Dense(extrapolated_days, activation='relu'),
        keras.layers.Dense(extrapolated_days, activation='linear'),
    ])
    optimizer = keras.optimizers.SGD(learning_rate=0.000001, momentum=0.9)
    lstmnn.compile(loss=keras.losses.binary_crossentropy, optimizer=optimizer, metrics=["mae"])
    #TODO need to normalize
    #add dummy dimension for Conv1D
    lstmnn.fit(np.array([training_datum]), np.array([label_datum]), verbose=1, epochs=2, batch_size=len(training_datum))
    # prediction_data = []
    # prediction_data.append([
    #     X[-1].year,
    #     X[-1].month,
    #     X[-1].day,
    #     X[-1].weekday(),
    #     Y[-1]
    # ])
    results = lstmnn.predict(np.array([training_datum[-2:-1]]))[-1].tolist()[-1]#lstmnn.predict(np.array([training_datum[-1*(extrapolated_days+1):-1]]))
    print(results)
    #unnormalize predictions
    predictions = list(map(lambda y: (y*largest_diff_from_zero)+average,results))
    base_date = X[-1]
    output = {}
    for prediction in predictions:
        base_date = base_date+timedelta(days=1)
        while base_date.weekday() in [5,6]: #skip Saturday and Sunday
            base_date = base_date+timedelta(days=1)
        output[str(datetime.timestamp(base_date))] = prediction
    print(output)
##############
    # from datetime import datetime
    # datum = Analyst([{'name':'Oversea-Chinese Banking Corporation Limited', 'symbol':'O39.SI'}], datetime(2020, 4, 4)).get()
    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(datum)
