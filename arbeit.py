from datetime import datetime

from mlogging import log
from mailer import Mailer
from year_high_low_analysis import Analyst

if __name__=='__main__':
	log('INFO', '***Start')
	try:
		Mailer().high_low_analysis_mail(Analyst().get())
	except:
		import traceback
		log('ERROR', 'There is an error: '+traceback.format_exc())
	log('INFO', '***End')
