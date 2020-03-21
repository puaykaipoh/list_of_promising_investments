from datetime import datetime

class Formater():

	def _format_number(self, num):
		return str(num)

	def _get_day_string(self, dt):
		return {
			0:'Mon',
			1:'Tue',
			2:'Wed',
			3:'Thu',
			4:'Fri',
			5:'Sat',
			6:'Sun'
		}[dt.weekday()]

	def _get_heat_color(self, num):# num must be between -1 and 1
		if 1 >= num and num > 0.9:
			return '#00ff00'
		elif 0.9 >= num and num > 0.8:
			return '#19ff19'
		elif 0.8 >= num and num > 0.7:
			return '#33ff33'
		elif 0.7 >= num and num > 0.6:
			return '#4cff4c'
		elif 0.6 >= num and num > 0.5:
			return '#66ff66'
		elif 0.5 >= num and num > 0.4:
			return '#7fff7f'
		elif 0.4 >= num and num > 0.3:
			return '#99ff99'
		elif 0.3 >= num and num > 0.2:
			return '#b2ffb2'
		elif 0.2 >= num and num > 0.1:
			return '#ccffcc'
		elif 0.1 >= num and num > 0:
			return '#e5ffe5'
		elif num == 0:
			return '#ffffff'
		elif 0 > num and num >= -0.1:
			return '#ffe5e5'
		elif -0.1 > num and num >= -0.2:
			return '#ffcccc'
		elif -0.2 > num and num >= -0.3:
			return '#ffb2b2'
		elif -0.3 > num and num >= -0.4:
			return '#ff9999'
		elif -0.4 > num and num >= -0.5:
			return '#ff7f7f'
		elif -0.5 > num and num >= -0.6:
			return '#ff6666'
		elif -0.6 > num and num >= -0.7:
			return '#ff4c4c'
		elif -0.7 > num and num >= -0.8:
			return '#ff3333'
		elif -0.8 > num and num >= -0.9:
			return '#ff1919'
		elif -0.9 > num and num >= -1:
			return '#ff0000'

	def _low_table(self, hl_datum):
		low = """<table style="border-collapse:collapse">
			<thead><tr style="background-color:#0099ff"><th></th>"""
		low += """<th>Name</th>"""
		low += """<th>Day</th>"""
		low += """<th>1 Year</th>"""
		low += """<th>2 Year</th>"""
		low += """<th>5 Year</th>"""
		low += """</tr></thead>
			<tbody>"""
		for i, dictionary in enumerate(hl_datum['low']):
			if i % 2 == 0:
				background_color = '#47d147'
			else:
				background_color = '#2eb82e'
			low += """<tr style='background-color:"""+background_color+"""'>"""
			low += """<td>"""+str(i)+"""</td>"""
			low += """<td>"""+dictionary['name']+' ('+dictionary['symbol']+""")</td>"""
			low += """<td>"""+self._format_number(dictionary['day'])+"""</td>"""
			low += """<td>"""+self._format_number(dictionary['1_year'])+"""</td>"""
			low += """<td>"""+self._format_number(dictionary['2_year'])+"""</td>"""
			low += """<td>"""+self._format_number(dictionary['5_year'])+"""</td>"""
			low += """</tr>"""
		low += """</tbody>
		</table>"""
		return low

	def _high_table(self, hl_datum):
		high = """<table style="border-collapse:collapse">
			<thead><tr style="background-color:#0099ff"><th></th>"""
		high += """<th>Name</th>"""
		high += """<th>Day</th>"""
		high += """<th>1 Year</th>"""
		high += """<th>2 Year</th>"""
		high += """<th>5 Year</th>"""
		high += """</tr></thead>
			<tbody>"""
		for i, dictionary in enumerate(hl_datum['high']):
			if i % 2 == 0:
				background_color = '#47d147'
			else:
				background_color = '#2eb82e'
			high += """<tr style='background-color:"""+background_color+"""'>"""
			high += """<td>"""+str(i)+"""</td>"""
			high += """<td>"""+dictionary['name']+' ('+dictionary['symbol']+""")</td>"""
			high += """<td>"""+self._format_number(dictionary['day'])+"""</td>"""
			high += """<td>"""+self._format_number(dictionary['1_year'])+"""</td>"""
			high += """<td>"""+self._format_number(dictionary['2_year'])+"""</td>"""
			high += """<td>"""+self._format_number(dictionary['5_year'])+"""</td>"""
			high += """</tr>"""
		high += """</tbody>
		</table>"""
		return high

	def _low_historical(self, hl_datum):
		values_display_name = {'day':'Day', '1_year':'1 Year', '2_year':'2 Year', '5_year':'5 Year'}
		low_historical = """<table style="border-collapse:collapse">
			<thead></thead>"""
		low_historical += """<tbody>"""
		for (symbol, name), d_list in hl_datum['historical']['low'].items():
			values = {'day':[], '1_year':[], '2_year':[], '5_year':[]}
			low_historical += """<tr>
				<td rowspan=5 colspan=1 style="background-color:#0099ff">"""+name+' ('+symbol+""")</td>
				<td rowspan=1 colspan=1 style="background-color:#00aaff">Date</td>"""
			d_list.sort(key=lambda d: d['current_date'])
			for d in d_list:
				low_historical += """<td rowspan=1 colspan=1 style="background-color:#00aaff">"""+datetime.strftime(d['current_date'],"%Y-%m-%d")+""" ("""+self._get_day_string(d['current_date'])+""")</td>"""
				values['day'].append(self._format_number(d['day']))
				values['1_year'].append(self._format_number(d['1_year']))
				values['2_year'].append(self._format_number(d['2_year']))
				values['5_year'].append(self._format_number(d['5_year']))
			low_historical += """</tr>"""
			for i, (k, v_list) in enumerate(values.items()):
				if i % 2 == 0:
					background_color = '#47d147'
				else:
					background_color = '#2eb82e'
				low_historical += """<tr style='background-color:"""+background_color+"""'><td rowspan=1 colspan=1>"""+values_display_name[k]+"""</td>"""
				for v in v_list:
					low_historical += """<td rowspan=1 colspan=1>"""+v+"""</td>"""
				low_historical += """</tr>"""
		low_historical +="""</tbody>
		</table>"""
		return low_historical

	def _high_historical(self, hl_datum):
		values_display_name = {'day':'Day', '1_year':'1 Year', '2_year':'2 Year', '5_year':'5 Year'}
		high_historical = """<table style="border-collapse:collapse">
			<thead></thead>"""
		high_historical += """<tbody>"""
		for (symbol, name), d_list in hl_datum['historical']['high'].items():
			values = {'day':[], '1_year':[], '2_year':[], '5_year':[]}
			high_historical += """<tr>
				<td rowspan=5 colspan=1 style="background-color:#0099ff">"""+name+' ('+symbol+""")</td>
				<td rowspan=1 colspan=1 style="background-color:#00aaff">Date</td>"""
			d_list.sort(key=lambda d: d['current_date'])
			for d in d_list:
				high_historical += """<td rowspan=1 colspan=1 style="background-color:#00aaff">"""+datetime.strftime(d['current_date'],"%Y-%m-%d")+""" ("""+self._get_day_string(d['current_date'])+""")</td>"""
				values['day'].append(self._format_number(d['day']))
				values['1_year'].append(self._format_number(d['1_year']))
				values['2_year'].append(self._format_number(d['2_year']))
				values['5_year'].append(self._format_number(d['5_year']))
			high_historical += """</tr>"""
			for i, (k, v_list) in enumerate(values.items()):
				if i % 2 == 0:
					background_color = '#47d147'
				else:
					background_color = '#2eb82e'
				high_historical += """<tr style='background-color:"""+background_color+"""'><td rowspan=1 colspan=1>"""+values_display_name[k]+"""</td>"""
				for v in v_list:
					high_historical += """<td rowspan=1 colspan=1>"""+v+"""</td>"""
				high_historical += """</tr>"""
		high_historical +="""</tbody>
		</table>"""
		return high_historical

	def _correlation(self, correlation_datum):
		correlation = """<table style="border-collapse:collapse">
			<thead></thead><tbody><tr><td></td>"""
		header_keys = list(map(lambda d: (d[0][0], d[0][1]), correlation_datum[0][2].items()))
		#header_keys.sort(key=lambda d: d[0]) #TOOD find out why it does not work
		for header_key in header_keys:
			correlation += """<td>"""+header_key[0]+"""("""+header_key[1]+"""</td>"""
		correlation += """</tr>"""
		for row_name, row_symbol, column_dictionary in correlation_datum:
			correlation += """<tr><td>"""+row_name+' ('+row_symbol+""")</td>"""
			for header_key in header_keys:
				value = column_dictionary.get(header_key, None)
				if value:
					correlation += """<td style='background-color:"""+self._get_heat_color(value)+"""'>"""+str(value)+"""</td>"""
				else:
					break
			correlation += """</tr>"""
		correlation += """</tbody></table>"""
		return correlation

	def _financial_stats(self, financial_stats_datum):
		financial_stats = """<table border="1"><thead><tr>"""
		for (content, rowspan, colspan) in financial_stats_datum.pop(0): # first row is header
			financial_stats += '<th rowspan="{}" colspan="{}">{}</th>'.format(rowspan, colspan, content)
		financial_stats += """</tr></thead><tbody>"""
		for row in financial_stats_datum:
			financial_stats += '<tr>'
			for (content, rowspan, colspan) in row:
				financial_stats += '<th rowspan="{}" colspan="{}">{}</th>'.format(rowspan, colspan, content)
			financial_stats += '</tr>'
		financial_stats += """</tbody></table>"""
		return financial_stats

	def daily_mail(self, hl_datum, correlation_datum, financial_stats_datum):
		low = self._low_table(hl_datum)
		high = self._high_table(hl_datum)
		low_historical = self._low_historical(hl_datum)
		high_historical = self._high_historical(hl_datum)
		correlation = self._correlation(correlation_datum)
		financial_stats = self._financial_stats(financial_stats_datum)
		html = """<table>
			<thead></thead>
			<tbody>
				<tr><td style='font-weight:800;font-size:22px'>Low</td></tr>
				<tr><td>{}</td></tr>
				<tr><td style='font-weight:800;font-size:22px'>High</td></tr>
				<tr><td>{}</td></tr>
				<tr><td style='font-weight:800;font-size:22px'>Financial Stats</td></tr>
				<tr><td>{}</td></tr>
				<tr><td style='font-weight:800;font-size:22px'>Historical Low</td></tr>
				<tr><td>{}</td></tr>
				<tr><td style='font-weight:800;font-size:22px'>Historical High</td></tr>
				<tr><td>{}</td></tr>
				<tr><td style='font-weight:800;font-size:22px'>Correlation</td></tr>
				<tr><td>{}</td></tr>
			</tbody>
		</table>""".format(low, high, financial_stats, low_historical, high_historical, correlation)
		return html