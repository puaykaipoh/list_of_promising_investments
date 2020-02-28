from datetime import datetime
import os

class Filer():

	def file(self, content):
		mails_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mails')
		if not os.path.isdir(mails_folder):
			os.makedirs(mails_folder)
		filename = datetime.strftime(datetime.utcnow(), "%Y%m%d%H%M%S%f") + '.html'
		file = open(os.path.join(mails_folder, filename), 'w')
		file.write(content)
		file.close()
