from bs4 import BeautifulSoup
import gzip
from html.parser import HTMLParser
import os
import random
import re
from time import sleep
from urllib.request import urlopen, Request

from mlogging import log


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
        self.sginvestors_url = 'https://sginvestors.io/analysts/sti-straits-times-index-constituents-target-price'
        self.NUMBER_OF_RETRY_CALLS = 8

    def get(self):
        data = self._get_from_sginvestors()
        if len(data) == 0:
            log('WARNING', 'sti_component not using from SGInvestors, trying yahoo')
            return _get_from_yahoo()
        else:
            return data

    def _get_from_yahoo(self):
        #req = urlopen(self.url)

        counter = 0
        while counter < self.NUMBER_OF_RETRY_CALLS:
            try:
                sleep(3*(random.random()+1.5))
                #req = urlopen(url)
                request = Request(
                    self.url,
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
                data = req.read()
            except:
                counter += 1
                import traceback
                log('ERROR', 'sti_component retry times '+str(counter+1)+' error:'+traceback.format_exc())
                sleep(3*(random.random()+1.5))
        #print(str(req.info().get('Content-Encoding')))
        try:
            data = gzip.decompress(data)
        except:
            log('INFO', 'cannot decompress, type: '+str(req.info().get('Content-Encoding')))
        #self.table_parser.feed(req.read().decode())
        self.table_parser.feed(data.decode())
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


    def _get_from_sginvestors(self):
        try:
            counter = 0
            while counter < self.NUMBER_OF_RETRY_CALLS:
              try:
                sleep(3*(random.random()+1.5))
                #req = urlopen(url)
                request = Request(
                  self.sginvestors_url,
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
                data = req.read()
                try:
                    data = gzip.decompress(data)
                except:
                    log('INFO', 'cannot decompress, type: '+str(req.info().get('Content-Encoding')))
                soup = BeautifulSoup(data.decode(), features="lxml")
                table = soup.find('table', id='stock-list-analyst-target-price')
                cells = table.find_all('td', {'class':'text-primary'})
                ######old code 202204052031
                # name_bracket_tickers = list(map(lambda cell: cell.find_all('a')[0].contents[0], cells))
                # data = []
                # for names_bracket_ticker in name_bracket_tickers:
                #     print('****', names_bracket_ticker)
                #     matches = matches = re.match("(.+)+\((\w+.SI)\)", names_bracket_ticker)
                #     if matches:
                #         groups = matches.groups()
                #         data.append({'symbol':groups[1], 'name':groups[0]})
                #     else:
                #         log('WARNING', f'sti_component no match {names_bracket_ticker}')
                #######old code 202204052031
                log('INFO', f"sti_components found {len(cells)} cells")
                data = []
                for cell in cells:
                    contents = cell.find_all('a')[0].contents
                    name = contents[0]
                    symbol = re.match("\(SGX:(\w+)\)", contents[2].contents[0]).groups()[0]+'.SI'
                    data.append({'symbol':symbol, 'name':name})
                return data
              except:
                counter += 1
                import traceback
                log('ERROR', 'SGInvestors.IO sti_component retry times '+str(counter+1)+' error:'+traceback.format_exc())
                sleep(3*(random.random()+1.5))
        except:
            log('ERROR', 'Failed to get from SGInvestors.IO')
            return []

    def parse_result(self, response):
        print(dir(response.selector))


if __name__=='__main__':
    data = STIComponents().get()
    #data = STIComponents()._get_from_sginvestors()
    print(len(data))
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)