from datetime import datetime, timedelta
from json import loads
from time import mktime
from urllib.parse import urlencode
from urllib.request import urlopen


class Ticker():
	BASE_URL = 'https://query1.finance.yahoo.com'

	def __init__(self, ticker):
		self.ticker = ticker

	def _call_url(self, params_dict):
		url = "{}/v8/finance/chart/{}?{}".format(self.BASE_URL, self.ticker, urlencode(params_dict))
		#print(url)
		req = urlopen(url)
		data = req.read()
		return loads(data)

	def _read_data(self):
		try:
			prices = self.json_data['chart']['result'][0]['indicators']
			quote = prices['quote'][0]
			return {'high':max(quote['high']), 
					'volume':sum(quote['volume']), 
					'close':quote['close'][-1],
					'open':quote['open'][0],
					'low':min(quote['low']),
					'adjclose':prices['adjclose'][0]['adjclose'][-1]}
		except:
			return None


	def get_day_data(self, start=None, end=None):
		if end == None:
			end = datetime.utcnow()
		if start == None:
			start = end - timedelta(days=1)
		start = int(mktime(start.timetuple()))
		end = int(mktime(end.timetuple()))
		self.json_data = self._call_url({"period1":start, "period2":end, "interval":'1d', "includePrePost":True, "events":"div,splits"})
		return self._read_data()

	def get_n_year_data(self, n=1, end=datetime.utcnow()):
		if end == None:
			end = datetime.utcnow()
		start = end - timedelta(days=365 * n)
		start = int(mktime(start.timetuple()))
		end = int(mktime(end.timetuple()))
		self.json_data = self._call_url({"period1":start, "period2":end, "interval":'3mo', "includePrePost":True, "events":"div,splits"})
		return self._read_data()


if __name__ == "__main__":
	ticker = Ticker('Z74.SI')
	print(ticker.get_n_year_data())