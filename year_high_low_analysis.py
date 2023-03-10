from datetime import datetime, timedelta
import pytz

from mlogging import log
from ticker_data import Ticker

class Analyst():
  datum = {'high':[], 'low':[]}

  def __init__(self, components, end):
    #if datetime.utcnow().weekday() in [5, 6]: #TODO this seems to be redundant code
    #	raise Exception('Its a week end')
    for i, dictionary in enumerate(components):
      try:
        log('INFO', dictionary['symbol']+' '+str(i+1)+'/'+str(len(components)))
        low_d, high_d = self._calculate_closeness(dictionary, end)
        if low_d is None or high_d is None:
          raise Exception('No date data')
        self.datum['high'].append(high_d)
        self.datum['low'].append(low_d)
      except:
        import traceback
        log('ERROR', '%s HL error : %s' % (dictionary, traceback.format_exc()))
    self.datum['high'].sort(key=lambda d:(100*100*100*100*100*d['5_year'])+(100*100*100*100*d['4_year'])+(100*100*100*d['3_year'])+(100*d['2_year'])+(d['1_year']))
    self.datum['low'].sort(key=lambda d:(100*100*100*100*100*d['5_year'])+(100*100*100*100*d['4_year'])+(100*100*100*d['3_year'])+(100*d['2_year'])+(d['1_year']))
    # historical = {'high':{}, 'low':{}}
    # log('INFO', 'HISTORICAL*********************')
    # for i, dictionary in enumerate(components):
    # 	number_of_days_of_data_needed = 10
    # 	current_date = end
    # 	ticker = Ticker(dictionary['symbol'])
    # 	key = (dictionary['symbol'], dictionary['name'])
    # 	historical['high'][key] = []
    # 	historical['low'][key] = []
    # 	while number_of_days_of_data_needed > 0:
    # 		current_date = current_date - timedelta(days=1)
    # 		if current_date.weekday() in [5, 6]:
    # 			continue
    # 		low_d, high_d = self._calculate_closeness(dictionary, end=current_date)
    # 		if low_d is not None and high_d is not None:
    # 			log('INFO', dictionary['symbol']+' '+datetime.strftime(current_date, '%Y-%m-%d')+' '+str(number_of_days_of_data_needed)+ ' '+str(i+1)+'/'+str(len(components)))
    # 			low_d['current_date'] = current_date
    # 			high_d['current_date'] = current_date
    # 			historical['high'][key].append(high_d)
    # 			historical['low'][key].append(low_d)
    # 			number_of_days_of_data_needed -= 1
    # self.datum['historical'] = historical

  def _calculate_closeness(self, dictionary, end=None):
    ticker = Ticker(dictionary['symbol'])
    day_data = ticker.get_day_data(start=None, end=end)
    if day_data == None:
      log('ERROR', 'did not get day data')
      return None, None
    one_year_data = ticker.get_n_year_data(n=1, end=end)
    if one_year_data == None:
      log('ERROR', 'did not get 1 year data')
      return None, None
    two_year_data = ticker.get_n_year_data(n=2, end=end)
    if two_year_data == None:
      log('ERROR', 'did not get 2 year data')
      return None, None
    three_year_data = ticker.get_n_year_data(n=3, end=end)
    if three_year_data == None:
      log('ERROR', 'did not get 3 year data')
      return None, None
    four_year_data = ticker.get_n_year_data(n=4, end=end)
    if four_year_data == None:
      log('ERROR', 'did not get 4 year data')
      return None, None
    five_year_data = ticker.get_n_year_data(n=5, end=end)
    if five_year_data == None:
      log('ERROR', 'did not get 5 year data')
      return None, None
    low_d = dict(dictionary)
    high_d = dict(dictionary)
    high_d.update({
      'day':day_data['high'],
      '1_year':(one_year_data['high']-day_data['high'])/one_year_data['high'],
      '2_year':(two_year_data['high']-day_data['high'])/two_year_data['high'],
      '3_year':(three_year_data['high']-day_data['high'])/three_year_data['high'],
      '4_year':(four_year_data['high']-day_data['high'])/four_year_data['high'],
      '5_year':(five_year_data['high']-day_data['high'])/five_year_data['high'],
    })
    low_d.update({
      'day':day_data['low'],
      '1_year':(day_data['low']-one_year_data['low'])/one_year_data['low'],
      '2_year':(day_data['low']-two_year_data['low'])/two_year_data['low'],
      '3_year':(three_year_data['low']-day_data['low'])/three_year_data['low'],
      '4_year':(four_year_data['low']-day_data['low'])/four_year_data['low'],
      '5_year':(day_data['low']-five_year_data['low'])/five_year_data['low'],
    })
    return low_d, high_d


  def get(self):
    return self.datum

if __name__=='__main__':
  from sti_components import STIComponents
  components = STIComponents().get()[0:3]
  end = datetime.utcnow().replace(tzinfo=pytz.utc)
  print(len(components))
  print(Analyst(components, end).get())