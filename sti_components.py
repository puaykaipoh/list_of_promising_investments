from bs4 import BeautifulSoup
from html.parser import HTMLParser
import os
from urllib.request import urlopen, Request

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
    self.sgx_url = 'https://www.sgx.com/indices/products/sti'

  def get(self):
    req = urlopen(self.url)
    self.table_parser.feed(req.read().decode())
    return self.table_parser.datum

  def _get_from_sgx(self, test_env=False): # TODO incomplete and not used
    if test_env:
      os.environ['GOOGLE_CHROME_BIN'] = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
      os.environ['CHROMEDRIVER_PATH'] = '.\\driver\\chromedriver.exe'
    else:
      os.environ['GOOGLE_CHROME_BIN'] = '/app/.apt/usr/bin/google_chrome'
      os.environ['CHROMEDRIVER_PATH'] = '/app/.chromedriver/bin/chromedriver'
    SELENIUM_DRIVER_NAME = 'chrome'
    SELENIUM_DRIVER_EXECUTABLE_PATH = os.environ.get('CHROMEDRIVER_PATH')
    SELENIUM_DRIVER_ARGUMENTS=['--headless', "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
    SELENIUM_BROWSER_EXECUTABLE_PATH = os.environ.get("GOOGLE_CHROME_BIN", "chromedriver")
    DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800
    }
    from scrapy_selenium import SeleniumRequest
    yield SeleniumRequest(url=self.sgx_url, callback=self.parse_result, wait_time=60)

  def parse_result(self, response):
    print(dir(response.selector))


if __name__=='__main__':
  data = STIComponents().get()
  print(len(data))
  import pprint
  pp = pprint.PrettyPrinter(indent=4)
  pp.pprint(data)