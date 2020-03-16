from datetime import datetime, timedelta
from html.parser import HTMLParser
from json import loads
from time import mktime
from urllib.parse import urlencode
from urllib.request import urlopen

from mlogging import log


class Ticker():
	BASE_URL = 'https://query1.finance.yahoo.com'
	SCRAPE_URL = 'https://finance.yahoo.com/quote'
	NUMBER_OF_RETRY_CALLS = 8

	def __init__(self, ticker):
		self.ticker = ticker

	def _call_url(self, params_dict):
		url = "{}/v8/finance/chart/{}?{}".format(self.BASE_URL, self.ticker, urlencode(params_dict))
		#print(url)
		counter = 0
		while counter < self.NUMBER_OF_RETRY_CALLS:
			try:
				req = urlopen(url)
				counter = self.NUMBER_OF_RETRY_CALLS
			except:
				counter += 1
				import traceback
				log('ERROR', '_call_url retry times '+str(counter+1)+' error:'+traceback.format_exc())
		data = req.read()
		return loads(data)

	def _read_data(self): # gets point data
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

	def _read_datum(self):# gets a range of datum
		results = self.json_data['chart']['result'][0]
		datum = list(map(lambda total_seconds:{'datetime':datetime.fromtimestamp(total_seconds)}, results['timestamp']))
		quotes = results['indicators']['quote'][0]
		for key in ['high', 'volume', 'close', 'open', 'low']:
			for i, value in enumerate(quotes[key]):
				datum[i][key] = value
		for i, value in enumerate(results['indicators']['adjclose'][0]['adjclose']):
			datum[i]['adjclose'] = value
		return datum

	def get_day_data(self, start=None, end=None):
		if end == None:
			end = datetime.utcnow()
		if start == None:
			start = end - timedelta(days=1)
		start = int(mktime(start.timetuple()))
		end = int(mktime(end.timetuple()))
		self.json_data = self._call_url({"period1":start, "period2":end, "interval":'1d'})#, "includePrePost":True, "events":"div,splits"})
		return self._read_data()

	def get_n_year_data(self, n=1, end=datetime.utcnow()):
		if end == None:
			end = datetime.utcnow()
		start = end - timedelta(days=365 * n)
		start = int(mktime(start.timetuple()))
		end = int(mktime(end.timetuple()))
		self.json_data = self._call_url({"period1":start, "period2":end, "interval":'3mo'})#, "includePrePost":True, "events":"div,splits"})
		return self._read_data()

	def get_daily_year_data(self, end=datetime.utcnow()):
		if end == None:
			end = datetime.utcnow()
		start = end - timedelta(days=365)
		start = int(mktime(start.timetuple()))
		end = int(mktime(end.timetuple()))
		self.json_data = self._call_url({"period1":start, "period2":end, "interval":'1d', "includePrePost":True, "events":"div,splits"})
		return self._read_datum()

	def get_financial_data(self):
		url = '{}/{}/financials'.format(self.SCRAPE_URL, self.ticker)
		req = urlopen(url)
		financial_parser = FinancialParser()
		financial_parser.feed(req.read().decode())
		return financial_parser.datum


class FinancialParser(HTMLParser): #https://finance.yahoo.com/quote/Z74.SI/financials?p=Z74.SI
	IN_HEADER_ROW = False
	IN_HEADER_CELL = False
	GET_HEADER_DATA = False
	GET_COLUMN_HEADER_DATA = False
	IN_DATA_TABLE = False

	def handle_starttag(self, tag, attrs):
		attrs = dict(attrs)
		if tag == 'div':
			if 'D(tbhg)' in attrs.get('class', []):
				self.IN_HEADER_ROW = True
			elif self.IN_HEADER_ROW and 'D(ib)' in attrs.get('class',[]):
				self.IN_HEADER_CELL = True
		elif tag == 'span' and 'Va(m)' in attrs.get('class', []):
			self.GET_COLUMN_HEADER_DATA = True
		elif self.IN_HEADER_CELL and tag=='span':
			self.GET_HEADER_DATA = True


	def handle_endtag(self, tag):
		pass

	def handle_data(self, data):
		if self.GET_HEADER_DATA:
			print('ROW HEADER', data)
			self.GET_HEADER_DATA = False
		elif self.GET_COLUMN_HEADER_DATA:
			print('COLUMN HEADER', data)
			self.GET_COLUMN_HEADER_DATA = False

if __name__ == "__main__":
	ticker = Ticker('Z74.SI')
	print(ticker.get_financial_data())