from datetime import datetime
import os

def log(level, message):
	logs_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
	if not os.path.isdir(logs_folder):
		os.makedirs(logs_folder)
	filename = datetime.strftime(datetime.utcnow(), "%Y%m%d") + '.txt'
	file = open(os.path.join(logs_folder, filename), 'a')
	stuff = datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S.%f')+' '+str(level)+' '+str(message)+'\r\n'
	print(stuff)
	file.write(stuff)
	file.close()