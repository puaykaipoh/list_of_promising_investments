from mlogging import log
from ticker_data import Ticker


class Analyst():
	datum = {}

	def __init__(self, components):#TODO assumes that components are not empty
		ranked_stats_table = self.compute_ranked_stats_table(components)
		self.datum = ranked_stats_table

	def compute_ranked_stats_table(self, components):
		stats = []
		#symbol_to_name = {}
		for i, component in enumerate(components):
			ticker = Ticker(component['symbol'])
			#symbol_to_name[component['symbol']] = component['name']
			stats.append((component['symbol'], self._flatten_dict(ticker.get_statistics_data())))
			log('INFO', 'converted '+str(i+1)+'/'+str(len(components)))
		key_symbol_value_rank = {}
		row_count = {}
		max_number_of_row_header = 0
		missing_keys = []
		for key, value in stats[0][1].items():#key: [ 'Trading information','Stock price history', 'Beta (5Y monthly)']
			symbol_value_tuples = []
			missing_one = False
			for symbol, flat_dict in stats:
				value_string = flat_dict.get(key)
				if value_string is None or value_string == 'N/A':
					missing_one = True
					break
				else:
					symbol_value_tuples.append((symbol, self._try_convert_to_num(value_string), value_string))
			#sort by value_string
			if not missing_one:
				max_number_of_row_header = max(len(key), max_number_of_row_header)
				for index, row_header in enumerate(key):
					if (index, row_header) in row_count:
						row_count[(index, row_header)] += 1
					else:
						row_count[(index, row_header)] = 1
				for rank, (symbol, v, value_string) in enumerate(sorted(symbol_value_tuples, key=lambda x: x[1])):
					#key_symbol_value_rank.append((key, symbol, value_string, rank))
					key_symbol_value_rank[(key, symbol)] = (value_string, rank)
			else:
				missing_keys.append(key)

		#TODO need to produce the table, list of list of tuple (row_header, how_many_rows, how_many_columns)
		table = []
		header = [("", 1, max_number_of_row_header)]
		for component in components:
			header.append((component['name']+' ('+component['symbol']+')', 1, 1))
		table.append(header)
		prev_row_header = [None] * max_number_of_row_header
		for key, value in sorted(stats[0][1].items(), key=lambda row: ''.join(row[0])):
			if key not in missing_keys:
				row = []
				#put in the row headers
				for row_header_index, row_header in enumerate(key):
					if prev_row_header[row_header_index] != row_header:
						prev_row_header[row_header_index] = row_header
						#clear the later prev_row_headers
						for i in range(row_header_index+1, len(prev_row_header)):
							prev_row_header[i] = None
						col_span = 1
						if row_header_index + 1 == len(key): #if last row_header
							col_span = max_number_of_row_header - row_header_index
						row.append((row_header, row_count[(row_header_index, row_header)], col_span))
				for component in components:
					value_rank = key_symbol_value_rank[(key, component['symbol'])]
					row.append(('[{}] {}'.format(value_rank[1], value_rank[0]), 1, 1))
				table.append(row)
		return table

	
	def _flatten_dict(self, stats_data):
		#stats_data is a dictionary of dictionary whose leaves are strings
		stack = [(stats_data, [])]
		results = []
		while len(stack) > 0:
			current = stack.pop()
			if type(current[0]) == dict:
				for key in current[0].keys():
					current_dict = current[0].copy()
					current_trail = current[1].copy()
					current_trail.append(key)
					stack.append((current_dict.get(key), current_trail))
			else:
				current_trail = current[1].copy()
				current_trail.append(current[0])
				results.append(current_trail)
		flat_dict = {}
		for row in results:
			flat_dict[tuple(row[:-1])] = row[-1] # everything before last one is key, last one is value
		return flat_dict
		#return results.sort(key=lambda x:''.join(x))

	def _try_convert_to_num(self, string):
		try:
			return float(string.replace('%', '').replace('B', '').replace('M', '').replace('k', ''))
		except:
			return string

	def get(self):
		return self.datum

if __name__=='__main__':
	financial_analyst = Analyst([
		{'name': 'Singapore Telecommunications Limited', 'symbol': 'Z74.SI'},
		{'name': 'Singapore Press Holdings Limited', 'symbol': 'T39.SI'},
		{'name': 'UOL Group Limited', 'symbol': 'U14.SI'}
		])

	from formater import Formater
	content = Formater()._financial_stats(financial_analyst.datum)
	from filer import Filer
	Filer().file(content)
	# import pprint
	# pp = pprint.PrettyPrinter(indent=2)
	# pp.pprint(financial_analyst.datum)