import smtplib
import requests

carriers = {
	'att'		:	'@mms.att.net',
	'tmobile'	:	'@tmomail.net',
	'verizon'	:	'@vtext.com',
	'sprint'	:	'@page.nextel.com',
	'lyca'		:	'@mms.us.lycamobile.com'
}

def send(user_message):
    # Replace the number with your own, or consider using an argument\dict for multiple people.
	to_number = '0000000000{}'.format(carriers['lyca'])
	auth = ('<email address>', 'password')
	Subject="Site Failure Update"
	message = (f"From: {auth[0]}\nTo:{to_number}\nSubject: {Subject}")
	message += f"\n\n{user_message}"
	# Establish a secure session with gmail's outgoing SMTP server using your gmail account
	server = smtplib.SMTP( "smtp.gmail.com", 587 )
	server.starttls()
	server.login(auth[0], auth[1])

	# Send text message through SMS gateway of destination number
	server.sendmail(auth[0], [to_number], message)
def check_ifup(url):
    r = requests.head(url)
    return r.status_code != 200	

import datetime
url = "URL to work"
for i in range(10):
	if check_ifup(url):
		error_text = 'Site: \n{} \nNOT Working:\n\n{} '.format(url,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		send(error_text)
		break