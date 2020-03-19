from html.parser import HTMLParser
from urllib.request import urlopen

class TableParser(HTMLParser):
	COLUMN_INDEX = None
	DATA = {}
	datum = []
	def handle_starttag(self, tag, attrs):
		if tag == 'tr':
			self.COLUMN_INDEX = 0
		elif tag == 'td':
			self.COLUMN_INDEX += 1

	def handle_endtag(self, tag):
		if tag == 'tr':
			self.COLUMN_INDEX = None
			DATA = dict(self.DATA)
			if len(DATA) > 0:
				self.datum.append(dict(self.DATA))
			DATA = {}

	def handle_data(self, data):
		if self.COLUMN_INDEX is not None:
			if self.COLUMN_INDEX == 1:
				self.DATA['symbol'] = data
			elif self.COLUMN_INDEX == 2:
				self.DATA['name'] = data

class STIComponents():

	def __init__(self):
		self.table_parser = TableParser()
		self.url = 'https://sg.finance.yahoo.com/quote/%5ESTI/components?p=%5ESTI'

	def get(self):
		req = urlopen(self.url)
		self.table_parser.feed(req.read().decode())
		return self.table_parser.datum


if __name__=='__main__':
	data = STIComponents().get()
	print(len(data))
	import pprint
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(data)