from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import gzip
from html.parser import HTMLParser
from json import loads
import locale
from time import mktime, sleep
import random
from urllib.parse import urlencode
from urllib.request import urlopen, Request

from mlogging import log


class Ticker():
	BASE_URL = 'https://query1.finance.yahoo.com'
	SCRAPE_URL = 'https://finance.yahoo.com/quote'
	SG_SCRAPE_URL = 'https://sg.finance.yahoo.com/quote'
	NUMBER_OF_RETRY_CALLS = 8

	def __init__(self, ticker):
		self.ticker = ticker

	def _call_url(self, params_dict):
		url = "{}/v8/finance/chart/{}?{}".format(self.BASE_URL, self.ticker, urlencode(params_dict))
		#print(url)
		counter = 0
		while counter < self.NUMBER_OF_RETRY_CALLS:
			try:
				sleep(3*(random.random()+1.5))
				#req = urlopen(url)
				request = Request(
					url,
					data=None,
					headers={
						"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
						"accept-encoding":"gzip, deflate, br",
						"accept-language":"en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
						"sec-fetch-dest":"document",
						"sec-fetch-mode":"navigate",
						"sec-fetch-site":"none",
						"sec-fetch-user":"?1",
						"upgrade-insecure-requests":"1",
						"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
					}
				)
				req = urlopen(request)
				counter = self.NUMBER_OF_RETRY_CALLS
			except:
				counter += 1
				import traceback
				log('ERROR', '_call_url retry times '+str(counter+1)+' error:'+traceback.format_exc())
				sleep(3*(random.random()+1.5))
		data = req.read()
		#print(str(req.info().get('Content-Encoding')))
		try:
			data = gzip.decompress(data)
		except:
			log('INFO', 'cannot decompress, type: '+str(req.info().get('Content-Encoding')))
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
		locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
		url = '{}/{}/financials'.format(self.SCRAPE_URL, self.ticker)
		req = urlopen(url)
		financial_parser = FinancialParser()
		financial_parser.feed(req.read().decode())
		#return financial_parser.datum
		return financial_parser.datum

	def get_statistics_data(self):
		locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
		url = '{}/{}/key-statistics'.format(self.SG_SCRAPE_URL, self.ticker)
		counter = 0
		while counter < self.NUMBER_OF_RETRY_CALLS:
			try:
				sleep(3*(random.random()+1.5))
				print(url)

				request = Request(
					url,
					data=None,
					headers={
						"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
						"accept-encoding":"gzip, deflate, br",
						"accept-language":"en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
						"sec-fetch-dest":"document",
						"sec-fetch-mode":"navigate",
						"sec-fetch-site":"none",
						"sec-fetch-user":"?1",
						"upgrade-insecure-requests":"1",
						"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
					}
				)
				req = urlopen(request)
			except:
				counter += 1
				import traceback
				log('ERROR', 'get_statistics_data retry times '+str(counter+1)+' error:'+traceback.format_exc())
				sleep(3*(random.random()+1.5))
				
		#req = urlopen(url)
		data = req.read()
		try:
			data = gzip.decompress(data)
			statistics = self.parse_stats(data)
			#print(data)
		except:
			log('INFO', 'get stats cannot decompress, type: '+str(req.info().get('Content-Encoding')))
			data = data.decode()
			statistics_parser = StatisticsParser()
			statistics_parser.feed(data)
			statistics = statistics_parser.datum
		################
		#file = open('D:\\random\\list_of_promising_investments\\test\\sample.html', 'wb')
		#file.write(data)
		#file.close()
		################
		#print(statistics)
		return statistics

	def parse_stats(self, content):
		dictionary = {}
		soup = BeautifulSoup(content, 'html.parser')
		for lg_table in soup.findAll("div", {"class":lambda x: x and 'Fl(' in x and 'smartphone_W(100%)' in x and 'W(50%)' in x}):
			title = lg_table.findAll('h2')[0].findAll('span')[0].text
			dictionary[title] = {}
			if 'valuation' in title.lower():
				for row in lg_table.findAll("tr"):
					cells = row.findAll("td")
					dictionary[title][cells[0].text] = cells[1].text
			else:
				for sm_table in lg_table.findAll("div", {"class":lambda x: x and "Pos(r)" in x and "Mt(10px)" in x}):
					sm_title = sm_table.findAll('h3')[0].findAll('span')[0].text
					dictionary[title][sm_title] = {}
					for row in sm_table.findAll("tr"):
						cells = row.findAll("td")
						dictionary[title][sm_title][cells[0].text] = cells[1].text
		return dictionary




class FinancialParser(HTMLParser): #https://finance.yahoo.com/quote/Z74.SI/financials?p=Z74.SI
	IN_TABLE = False
	IN_ROW = False
	GET_DATA = False
	IN_TABLE_DIV_COUNT = 1
	ROW_DIV_COUNT = 0
	ROW_INDEX = 0
	CELL_INDEX = 0
	HEADERS = {}
	CURRENT_ROW_HEADER = None
	datum = {}

	def handle_starttag(self, tag, attrs):
		attrs = dict(attrs)
		if self.IN_TABLE:
			if tag == 'div':
				self.IN_TABLE_DIV_COUNT +=1
				if self.IN_ROW:
					self.ROW_DIV_COUNT += 1
			if "D(tbr)" in attrs.get('class', []):
				self.IN_ROW = True
				self.ROW_INDEX += 1
				self.ROW_DIV_COUNT += 1
			elif self.IN_ROW and (("D(ib)" in attrs.get('class', [])) or ("D(tbc)" in attrs.get('class', []))):
				self.GET_DATA = True
		elif "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)" in attrs.get('class', []):
			self.IN_TABLE = True


	def handle_endtag(self, tag):
		if self.IN_TABLE and tag == 'div':
			self.IN_TABLE_DIV_COUNT -= 1
			if self.IN_TABLE_DIV_COUNT == 0:
				self.IN_TABLE = False
			if self.IN_ROW:
				self.ROW_DIV_COUNT -= 1
				if self.ROW_DIV_COUNT == 0:
					self.IN_ROW = False
					self.CELL_INDEX = 0
					# print('found end row')

	def handle_data(self, data):
		if self.IN_TABLE and self.GET_DATA and len(data)<=128:
			# print(self.ROW_INDEX, self.CELL_INDEX, data)
			if self.ROW_INDEX == 1:
				self.HEADERS[self.CELL_INDEX] = data
			else:
				if self.CELL_INDEX == 0:
					self.CURRENT_ROW_HEADER = data
				else:
					existing = self.datum.get(self.HEADERS[self.CELL_INDEX], {})
					try:
						num = locale.atoi(data)
					except:
						num = None
					existing[self.CURRENT_ROW_HEADER] = num
					self.datum[self.HEADERS[self.CELL_INDEX]] = existing
			self.CELL_INDEX += 1


class StatisticsParser(HTMLParser):
	IN_TABLE = False
	IN_TABLE_TABLE_COUNT = 0
	IN_HEADER = True
	HEADERS = {}
	HEADER_CELL_INDEX = 0
	BODY_CELL_INDEX = 0
	ROW_HEADER = None
	VALUATION_MEASURES_DATUM = {}
	datum = {}
	GET_TITLE = False
	GET_SUBTITLE = False
	TITLE = None
	SUBTITLE = None

	def handle_starttag(self, tag, attrs):
		attrs = dict(attrs)
		if self.IN_TABLE:
			if tag == 'thead':
				self.IN_HEADER = True
		elif tag == 'table' and 'W(100%) Bdcl(c)' in attrs.get('class', []):
			self.IN_TABLE = True
			self.IN_TABLE_TABLE_COUNT += 1
		elif tag == 'h2':
			self.GET_TITLE = True
		elif tag == 'h3':
			self.GET_SUBTITLE = True

	def handle_endtag(self, tag):
		if self.IN_TABLE:
			if tag == 'table':
				self.IN_TABLE_TABLE_COUNT -= 1
				if self.IN_TABLE_TABLE_COUNT == 0:
					self.IN_TABLE = False
			elif tag == 'thead':
				self.IN_HEADER = False
			elif tag == 'tr':
				self.BODY_CELL_INDEX = 0
				self.HEADER_CELL_INDEX = 0
		
	def handle_data(self, data):
		if self.GET_TITLE:
			self.TITLE = data
			self.GET_TITLE = False
			self.datum[self.TITLE] = {}
		elif self.GET_SUBTITLE:
			self.SUBTITLE = data
			self.GET_SUBTITLE = False
			self.datum[self.TITLE][self.SUBTITLE] = {}
		if self.IN_TABLE:
			#print(self.TITLE)
			if self.TITLE == '   ####Valuation Measures': #TODO does not work
				#print(self.BODY_CELL_INDEX, data)
				if self.IN_HEADER:
					#print(self.HEADERS, data, self.HEADER_CELL_INDEX)
					self.HEADERS[self.HEADER_CELL_INDEX] = data
					self.HEADER_CELL_INDEX += 1
				else:
					if self.BODY_CELL_INDEX == 0:
						self.ROW_HEADER = data
					else:
						existing = self.datum[self.TITLE].get(self.HEADERS[self.BODY_CELL_INDEX], {})
						existing[self.ROW_HEADER] = data
						self.datum[self.TITLE][self.HEADERS[self.BODY_CELL_INDEX]] = existing
			elif self.TITLE in ['Valuation measures','Financial highlights', 'Trading information']:
				#print(self.BODY_CELL_INDEX, data)
				if self.BODY_CELL_INDEX == 0:
					self.ROW_HEADER = data
				else:
					if self.SUBTITLE:
						self.datum[self.TITLE][self.SUBTITLE][self.ROW_HEADER] = data
					else:
						self.datum[self.TITLE][self.ROW_HEADER] = data
			self.BODY_CELL_INDEX += 1


if __name__ == "__main__":
	#https://query1.finance.yahoo.com/v8/finance/chart/Z74.SI?period1=1582435961&period2=1582522361&interval=1d&includePrePost=True&events=div%2Csplits
	ticker = Ticker('Z74.SI')
	financial_data = ticker.get_statistics_data()#ticker.get_financial_data()
	import pprint
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(financial_data)
	#file = open('D:\\random\\list_of_promising_investments\\test\\sample.html', 'rb')
	#dictionary = ticker.parse_stats(file.read())
	#import pprint
	#pp = pprint.PrettyPrinter(indent=4)
	#pp.pprint(dictionary)