from datetime import datetime
import pytz
import sys

from mlogging import log

if __name__=='__main__':
  log('INFO', '***Start')
  end = datetime.utcnow().replace(tzinfo=pytz.utc)
  if len(sys.argv) > 1:
    end = datetime.strptime(sys.argv[1], '%Y/%m/%d')
  if end.weekday() in [5,6]:
    log('INFO', datetime.strftime(end, '%Y/%m/%d')+' is a weekend')
    sys.exit()
  try:
    from sti_components import STIComponents
    interested_equities = STIComponents().get()
    if len(sys.argv) > 1 and '--test' in sys.argv:#use a smaller set of equities for testing
      log('INFO', 'testing*********************')
      #interested_equities = [
        #{'name':'Singapore Telecommunications Limited', 'symbol':'Z74.SI'},
        #{'name':'Oversea-Chinese Banking Corporation Limited', 'symbol':'O39.SI'},
        #{'name':'SATS Ltd.', 'symbol':'S58.SI'},
        #{'name':'CapitaLand Limited', 'symbol':'C31.SI'}
      #]
      interested_equities = interested_equities[0:3]
      log('INFO', interested_equities)
    else:
      log('INFO', 'this is not a test')
    from year_high_low_analysis import Analyst as HL_Analyst
    hl_datum = HL_Analyst(interested_equities, end).get()
    log('INFO', 'Finished HL analysis')
    from correlation_analysis import Analyst as CR_Analyst
    correlation_datum = CR_Analyst(interested_equities, end).get()
    log('INFO', 'Finished CR analysis')
    from financial_analysis import Analyst as FS_Analyst
    financial_stats_datum = FS_Analyst(interested_equities).get()
    log('INFO', 'Finished FS analysis')
    from regression_analysis import Analyst as RA_Analyst
    segmented_datum = RA_Analyst(interested_equities, end).get()
    log('INFO', 'Finished RA analysis')
    from seasonal_analysis import Analyst as SA_Analyst
    seasonal_datum = SA_Analyst(interested_equities, end).get()
    log('INFO', 'Finished SA analysis')
    from formater import Formater
    content = Formater().daily_mail(hl_datum, correlation_datum, financial_stats_datum, segmented_datum, seasonal_datum)
    if len(sys.argv) == 1 or '--test' not in sys.argv:
      from mailer import Mailer
      mfunction = Mailer().send_mail
      margs = [["puaykaipoh@gmail.com", "charissatanweiyi@gmail.com"], 
        "kai@arbeit.com", 
        "STI Analysis Report "+datetime.strftime(datetime.utcnow(), "%Y %b %d"), 
        content]
    else:
      from filer import Filer
      mfunction = Filer().file
      margs = [content]
    mfunction(*margs)
  except:
    import traceback
    log('ERROR', 'There is an error: '+traceback.format_exc())
  log('INFO', '***End')
