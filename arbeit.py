from datetime import datetime
import sys

from mlogging import log

if __name__=='__main__':
	log('INFO', '***Start')
	end = datetime.utcnow()
	if len(sys.argv) > 1:
		end = datetime.strptime(sys.argv[1], '%Y/%m/%d')
	try:
		from sti_components import STIComponents
		interested_equities = STIComponents().get()
		from year_high_low_analysis import Analyst as HL_Analyst
		hl_datum = HL_Analyst(interested_equities, end).get()
		log('INFO', 'Finished HL analysis')
		from correlation_analysis import Analyst as CR_Analyst
		correlation_datum = CR_Analyst(interested_equities, end).get()
		log('INFO', 'Finished CR analysis')
		from formater import Formater
		content = Formater().daily_mail(hl_datum, correlation_datum)
		if len(sys.argv) == 1:
			from mailer import Mailer
			mfunction = Mailer().send_mail
			margs = [["puaykaipoh@gmail.com"], 
				"donotreply@arbeit.com", 
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
