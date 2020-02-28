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


	def send_mail(self, to_adds, from_add, subject, content):
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
