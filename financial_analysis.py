from mlogging import log
from ticker_data import Ticker


class Analyst():
	datum = {}

	def __init__(self, components):#TODO assumes that components are not empty
		ranked_stats_table = self.compute_ranked_stats_table(components)

	def compute_ranked_stats_table(self, components):
		stats = []
		symbol_to_name = {}
		for i, component in enumerate(components):
			ticker = Ticker(component['symbol'])
			symbol_to_name[component['symbol']] = component['name']
			stats.append((component['symbol'], self._flatten_dict(ticker.get_statistics_data())))
			log('INFO', 'converted '+str(i)+'/'+str(len(components)))
		key_symbol_value_rank = []
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
				for rank, (symbol, v, value_string) in sorted(symbol_value_tuples, key=lambda x: x[1]):
					key_symbol_value_rank.append((key, symbol, value_string, rank))
		#TODO need to count each key how many rows it occupy
	
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
			flat_dict[row[:-1]] = row[-1] # everything before last one is key, last one is value
		return results

	def _try_convert_to_num(string):
		return float(string.replace('%', '').replace('B', '').replace('M', '').replace('k', ''))

if __name__=='__main__':
	financial_analyst = Analyst([
		{'name': 'Singapore Telecommunications Limited', 'symbol': 'Z74.SI'},
		{'name': 'Singapore Press Holdings Limited', 'symbol': 'T39.SI'},
		{'name': 'UOL Group Limited', 'symbol': 'U14.SI'}
		])
	# import pprint
	# pp = pprint.PrettyPrinter(indent=2)
	# pp.pprint(financial_analyst.datum)