from datetime import datetime
import math
import xml.etree.cElementTree as ET

from mlogging import log

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
      return '#00ff0044'
    elif 0.9 >= num and num > 0.8:
      return '#19ff1944'
    elif 0.8 >= num and num > 0.7:
      return '#33ff3344'
    elif 0.7 >= num and num > 0.6:
      return '#4cff4c44'
    elif 0.6 >= num and num > 0.5:
      return '#66ff6644'
    elif 0.5 >= num and num > 0.4:
      return '#7fff7f44'
    elif 0.4 >= num and num > 0.3:
      return '#99ff9944'
    elif 0.3 >= num and num > 0.2:
      return '#b2ffb244'
    elif 0.2 >= num and num > 0.1:
      return '#ccffcc44'
    elif 0.1 >= num and num > 0:
      return '#e5ffe544'
    elif num == 0:
      return '#ffffff44'
    elif 0 > num and num >= -0.1:
      return '#ffe5e544'
    elif -0.1 > num and num >= -0.2:
      return '#ffcccc44'
    elif -0.2 > num and num >= -0.3:
      return '#ffb2b244'
    elif -0.3 > num and num >= -0.4:
      return '#ff999944'
    elif -0.4 > num and num >= -0.5:
      return '#ff7f7f44'
    elif -0.5 > num and num >= -0.6:
      return '#ff666644'
    elif -0.6 > num and num >= -0.7:
      return '#ff4c4c44'
    elif -0.7 > num and num >= -0.8:
      return '#ff333344'
    elif -0.8 > num and num >= -0.9:
      return '#ff191944'
    elif -0.9 > num and num >= -1:
      return '#ff000044'

  def _low_table(self, hl_datum):
    low = """<table style="border-collapse:collapse">
      <thead><tr style="background-color:#0099ff44"><th></th>"""
    low += """<th>Name</th>"""
    low += """<th>Day</th>"""
    low += """<th>1 Year</th>"""
    low += """<th>2 Year</th>"""
    low += """<th>5 Year</th>"""
    low += """</tr></thead>
      <tbody>"""
    for i, dictionary in enumerate(hl_datum['low']):
      if i % 2 == 0:
        background_color = '#47d14744'
      else:
        background_color = '#2eb82e44'
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
      <thead><tr style="background-color:#0099ff44"><th></th>"""
    high += """<th>Name</th>"""
    high += """<th>Day</th>"""
    high += """<th>1 Year</th>"""
    high += """<th>2 Year</th>"""
    high += """<th>5 Year</th>"""
    high += """</tr></thead>
      <tbody>"""
    for i, dictionary in enumerate(hl_datum['high']):
      if i % 2 == 0:
        background_color = '#47d14744'
      else:
        background_color = '#2eb82e44'
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
        <td rowspan=5 colspan=1 style="background-color:#0099ff44">"""+name+' ('+symbol+""")</td>
        <td rowspan=1 colspan=1 style="background-color:#00aaff44">Date</td>"""
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
          background_color = '#47d14744'
        else:
          background_color = '#2eb82e44'
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
        <td rowspan=5 colspan=1 style="background-color:#0099ff44">"""+name+' ('+symbol+""")</td>
        <td rowspan=1 colspan=1 style="background-color:#00aaff44">Date</td>"""
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
          background_color = '#47d14744'
        else:
          background_color = '#2eb82e44'
        high_historical += """<tr style='background-color:"""+background_color+"""'><td rowspan=1 colspan=1>"""+values_display_name[k]+"""</td>"""
        for v in v_list:
          high_historical += """<td rowspan=1 colspan=1>"""+v+"""</td>"""
        high_historical += """</tr>"""
    high_historical +="""</tbody>
    </table>"""
    return high_historical

  def _correlation(self, correlation_datum):
    try:
      correlation_datum[0][2] #TODO this is the error correlation_datum is []
    except:
      log('WARNING', 'correlation_datum[0][2] is error %s' % correlation_datum)
      return ""
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

  def _segmented_linear_regression(self, segmented_datum):
    segmented = ET.Element("table")
    segmented.set('border', '1')
    body = ET.SubElement(segmented, "tbody")
    for (ticker, name), datum in segmented_datum.items():
      row = ET.SubElement(body, "tr")
      ET.SubElement(row, "td").text = name+" ("+ticker+")"#first column
      second_column = ET.SubElement(row, "td")
      inner_trends_table = ET.SubElement(second_column, "table")
      inner_trends_table.set('border', '1')
      inner_trends_table_header = ET.SubElement(inner_trends_table, "thead")
      inner_header_row = ET.SubElement(inner_trends_table_header, "tr")
      ET.SubElement(inner_header_row, "th").text = "Overall"
      for i in range(0, len(datum['segments'])):
        ET.SubElement(inner_header_row, "th").text = "Trend "+str(i)
      inner_trends_table_body = ET.SubElement(inner_trends_table, "tbody")
      individual_trend_properties_row = ET.SubElement(inner_trends_table_body, 'tr')
      overall_cell = ET.SubElement(individual_trend_properties_row, 'td')
      overall_cell.text = str(datum['overall_trend'])#overall cell
      if not math.isnan(datum['overall_trend']):
        if datum['overall_trend'] > 0:
          overall_cell.set('style','background-color:#00ff0044;')
        else:
          overall_cell.set('style','background-color:#ff000044;')
      for segment in datum['segments']:
        trend_cell = ET.SubElement(individual_trend_properties_row, 'td')
        trend_table = ET.SubElement(trend_cell, 'table')
        trend_table.set('border', '1')
        trend_table_body = ET.SubElement(trend_table, 'tbody')
        for tag, info in segment.items():
          trend_info_row = ET.SubElement(trend_table_body, 'tr')
          if tag == 'percentage_slope':
            if info > 0:
              trend_table_body.set('style','background-color:#00ff0044;') #green
            else:
              trend_table_body.set('style','background-color:#ff000044;') #red
          ET.SubElement(trend_info_row, 'td').text = str(tag)
          ET.SubElement(trend_info_row, 'td').text = str(info)
    return ET.tostring(segmented, encoding='utf8', method='html')

  def _seasonal_forecast(self, seasonal_datum):
    season = ET.Element("table")
    season.set('border', '1')
    body = ET.SubElement(season, "tbody")
    for (ticker, name), datum in seasonal_datum.items():
      row = ET.SubElement(body, "tr")
      ET.SubElement(row, "td").text = name+" ("+ticker+")"#first column
      second_column = ET.SubElement(row, "td")
      inner_table = ET.SubElement(second_column, "table")
      inner_table.set('border', '1')
      inner_table_header = ET.SubElement(inner_table, 'thead')
      inner_table_header_row = ET.SubElement(inner_table_header, "tr")
      ET.SubElement(inner_table_header_row, "th") # a space for the name of the regressor
      inner_table_body = ET.SubElement(inner_table, 'tbody')
      #find smallest set of datetime
      smallest_set_of_datetime = set()
      for regression_name, forecast_datum in datum.items():
        if len(smallest_set_of_datetime) == 0:
          smallest_set_of_datetime = set(forecast_datum.keys())
        else:
          smallest_set_of_datetime = smallest_set_of_datetime.intersection(forecast_datum.keys())
      smallest_set_of_datetime = sorted(list(smallest_set_of_datetime))
      for dt in smallest_set_of_datetime:
        ET.SubElement(inner_table_header_row, "th").text = datetime.strftime(datetime.fromtimestamp(float(dt)), "%Y-%m-%d")
      for regression_name, forecast_datum in datum.items():
        regressor_row = ET.SubElement(inner_table_body, "tr")
        ET.SubElement(regressor_row, 'td').text = regression_name
        for dt in smallest_set_of_datetime:
          ET.SubElement(regressor_row, 'td').text = str(forecast_datum[dt])
    return ET.tostring(season, encoding='utf8', method='html')



  def daily_mail(self, hl_datum, correlation_datum, financial_stats_datum, segmented_datum, seasonal_datum):
    low = self._low_table(hl_datum)
    high = self._high_table(hl_datum)
    trends = self._segmented_linear_regression(segmented_datum)
    #low_historical = self._low_historical(hl_datum)
    #high_historical = self._high_historical(hl_datum)
    seasons = self._seasonal_forecast(seasonal_datum)
    correlation = self._correlation(correlation_datum)
    financial_stats = self._financial_stats(financial_stats_datum)
    html = """<table>
      <thead></thead>
      <tbody>
        <tr><td style='font-weight:800;font-size:22px'>Low</td></tr>
        <tr><td>{}</td></tr>
        <tr><td style='font-weight:800;font-size:22px'>High</td></tr>
        <tr><td>{}</td></tr>
        <tr><td style='font-weight:800;font-size:22px'>Trends</td></tr>
        <tr><td>{}</td></tr>
        <tr><td style='font-weight:800;font-size:22px'>Seasons</td></tr>
        <tr><td>{}</td></tr>
        <tr><td style='font-weight:800;font-size:22px'>Financial Stats</td></tr>
        <tr><td>{}</td></tr>"""
        #<tr><td style='font-weight:800;font-size:22px'>Historical Low</td></tr>
        #<tr><td>{}</td></tr>
        #<tr><td style='font-weight:800;font-size:22px'>Historical High</td></tr>
        #<tr><td>{}</td></tr>
    html += """
        <tr><td style='font-weight:800;font-size:22px'>Correlation</td></tr>
        <tr><td>{}</td></tr>
      </tbody>
    </table>"""
    html = html.format(
      low, 
      high, 
      trends, 
      seasons,
      financial_stats, 
      #low_historical, 
      #high_historical, 
      correlation)
    return html

if __name__=='__main__':
    interested_equities = [
      #{'name':'Singapore Telecommunications Limited', 'symbol':'Z74.SI'},
      {'name':'Oversea-Chinese Banking Corporation Limited', 'symbol':'O39.SI'},
      # {'name':'SATS Ltd.', 'symbol':'S58.SI'},
      # {'name':'CapitaLand Limited', 'symbol':'C31.SI'}
    ]
    #################TODO for testing
    from seasonal_analysis import Analyst as SF_Analyst
    from datetime import datetime
    end = datetime(2020, 6, 11)
    segmented_datum = SF_Analyst(interested_equities, end).get()
    formater = Formater()
    trends = formater._seasonal_forecast(segmented_datum)
    file = open('D:\\random\\list_of_promising_investments\\seasonal_testing.html', 'w')
    from bs4 import BeautifulSoup
    file.write(BeautifulSoup(trends).prettify())
    file.close()
    #################TODO for testing