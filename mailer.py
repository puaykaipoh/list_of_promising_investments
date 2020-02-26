import base64
from datetime import datetime
from mlogging import log
import os
import smtplib
import ssl

class Mailer():

	def __init__(self, kind='SENDGRID'):
		self.kind = kind
		if kind == 'SENDGRID':
			from sendgrid import SendGridAPIClient
			log('INFO', 'api key : '+os.environ.get('SENDGRID_API_KEY'))
			self.service =  SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

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

	def high_low_analysis_mail(self, datum):
		low = """<table style="border-collapse:collapse">
			<thead><tr style="background-color:#0099ff"><th></th>"""
		low += """<th>Name</th>"""
		low += """<th>Day</th>"""
		low += """<th>1 Year</th>"""
		low += """<th>2 Year</th>"""
		low += """<th>5 Year</th>"""
		low += """</tr></thead>
			<tbody>"""
		for i, dictionary in enumerate(datum['low']):
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

		high = """<table style="border-collapse:collapse">
			<thead><tr style="background-color:#0099ff"><th></th>"""
		high += """<th>Name</th>"""
		high += """<th>Day</th>"""
		high += """<th>1 Year</th>"""
		high += """<th>2 Year</th>"""
		high += """<th>5 Year</th>"""
		high += """</tr></thead>
			<tbody>"""
		for i, dictionary in enumerate(datum['high']):
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

		values_display_name = {'day':'Day', '1_year':'1 Year', '2_year':'2 Year', '5_year':'5 Year'}
		low_historical = """<table border="1">
			<thead></thead>"""
		low_historical += """<tbody>"""
		for (symbol, name), d_list in datum['historical']['low'].items():
			values = {'day':[], '1_year':[], '2_year':[], '5_year':[]}
			low_historical += """<tr>
				<td rowspan=5 colspan=1>"""+name+' ('+symbol+""")</td>
				<td rowspan=1 colspan=1>Date</td>"""
			for d in d_list:
				low_historical += """<td rowspan=1 colspan=1>"""+datetime.strftime(d['current_date'],"%Y-%m-%d")+""" ("""+self._get_day_string(d['current_date'])+""")</td>"""
				values['day'].append(self._format_number(d['day']))
				values['1_year'].append(self._format_number(d['1_year']))
				values['2_year'].append(self._format_number(d['2_year']))
				values['5_year'].append(self._format_number(d['5_year']))
			low_historical += """</tr>"""
			for k, v_list in values.items():
				low_historical += """<tr><td rowspan=1 colspan=1>"""+values_display_name[k]+"""</td>"""
				for v in v_list:
					low_historical += """<td rowspan=1 colspan=1>"""+v+"""</td>"""
				low_historical += """</tr>"""
		low_historical +="""</tbody>
		</table>"""

		high_historical = """<table border="1">
			<thead></thead>"""
		high_historical += """<tbody>"""
		for (symbol, name), d_list in datum['historical']['high'].items():
			values = {'day':[], '1_year':[], '2_year':[], '5_year':[]}
			high_historical += """<tr>
				<td rowspan=5 colspan=1>"""+name+' ('+symbol+""")</td>
				<td rowspan=1 colspan=1>Date</td>"""
			for d in d_list:
				high_historical += """<td rowspan=1 colspan=1>"""+datetime.strftime(d['current_date'],"%Y-%m-%d")+""" ("""+self._get_day_string(d['current_date'])+""")</td>"""
				values['day'].append(self._format_number(d['day']))
				values['1_year'].append(self._format_number(d['1_year']))
				values['2_year'].append(self._format_number(d['2_year']))
				values['5_year'].append(self._format_number(d['5_year']))
			high_historical += """</tr>"""
			for k, v_list in values.items():
				high_historical += """<tr><td rowspan=1 colspan=1>"""+values_display_name[k]+"""</td>"""
				for v in v_list:
					high_historical += """<td rowspan=1 colspan=1>"""+v+"""</td>"""
				high_historical += """</tr>"""
		high_historical +="""</tbody>
		</table>"""

		html = """<table>
			<thead></thead>
			<tbody>
				<tr><td style='font-weight:800;font-size:22px'>Low</td></tr>
				<tr><td>{}</td></tr>
				<tr><td style='font-weight:800;font-size:22px'>High</td></tr>
				<tr><td>{}</td></tr>
				<tr><td style='font-weight:800;font-size:22px'>Historical Low</td></tr>
				<tr><td>{}</td></tr>
				<tr><td style='font-weight:800;font-size:22px'>Historical High</td></tr>
				<tr><td>{}</td></tr>
			</tbody>
		</table>""".format(low, high, low_historical, high_historical)
		self.send_mail(["puaykaipoh@gmail.com", "charissatanweiyi@gmail.com"], 
			"donotreply@arbeit.com", 
			"STI HL Closeness "+datetime.strftime(datetime.utcnow(), "%Y %b %d"), 
			html)

	def send_mail(self, to_adds, from_add, subject, content):
		######
		# import os 
		# mails_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mails')
		# if not os.path.isdir(mails_folder):
		# 	os.makedirs(mails_folder)
		# filename = datetime.strftime(datetime.utcnow(), "%Y%m%d%H%M%S%f") + '.html'
		# file = open(os.path.join(mails_folder, filename), 'w')
		# file.write(content)
		# file.close()
		######
		if self.kind == 'SENDGRID':
			from sendgrid.helpers.mail import Mail
			message = Mail(
				from_email=from_add,
				to_emails=', '.join(to_adds),
				subject=subject,
				html_content=content)
			response = self.service.send(message)
			log('INFO', response.status_code)
			log('INFO', response.body)
			log('INFO', response.headers)

