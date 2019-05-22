import sqlite3,requests,smtplib,time
from datetime import datetime
from datetime import timedelta
from  user_credentials import *
from constants import *

carriers = {
	'att'		:	'@mms.att.net',
	'tmobile'	:	'@tmomail.net',
	'verizon'	:	'@vtext.com',
	'sprint'	:	'@page.nextel.com',
	'lyca'		:	'@mms.us.lycamobile.com'
}

def check_ifup(url):
    return requests.head(url).status_code != 200	


def send_email(url,email):

    time = datetime.now().strftime("%H:%M:%S %m-%d-%Y")
    error_text = f"The Site {url} is not responding to the HTTP requests to the site at {time}. \n Please note there is a SMS sent to the registered number as well.\n The logger will resume monitoring this site again in 6 hours. \nThanks-\nSite Failure Team."
        
    auth = (gmail_account, password)
    Subject = f"Site Failure Detected for {url}"
    message = (f"From: {auth[0]}\nTo:{email}\nSubject: {Subject}")
    message += f"\n\n{error_text}"
    server = smtplib.SMTP( smtp_gmail, 587 )
    server.starttls()
    server.login(auth[0], auth[1])
    server.sendmail(auth[0], [email], message)
    return

def send_sms(url,phone,carrier):
    error_text = 'Site: \n{} \nNOT Working:\n\n{} '.format(url,datetime.now().strftime('%Y-%m-%d %H:%M:%S'))    
    to_number = '+1{}{}'.format("".join(phone.split('-')),carriers[carrier])
    print(f"sending the text to {to_number}")
    auth = (gmail_account, password)
    
    # message = MIMEMultipart("alternative")
    # message['From'] = auth[0]
    # message['To'] = to_number
    # message['Subject'] = 'Site Down'

    Subject="Site Failure Detected"
    message = (f"From: {auth[0]}\nTo:{to_number}\nSubject: {Subject}")
    message += f"\n\n{error_text}"

    # message.attach(MIMEText(user_message,"plain"))
    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP( smtp_gmail, 587 )
    server.starttls()
    server.login(auth[0], auth[1])

    # Send text message through SMS gateway of destination number
    server.sendmail(auth[0], [to_number], message)
    return 


def update_time(url,time):
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.execute('''update mail_record set time = ? where url=?''',(time,url))
    con.commit()
    con.close()

def send_messages():
    con = sqlite3.connect(database)
    cur = con.cursor()
    delete_counter = 0
    while True:
        time.sleep(1)
        if delete_counter > 100:
            cur.execute('''delete from mail_record where strftime(?,time) <= ?''',("%Y-%m-%d %H:%M:%S",(datetime.now()-timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')))
            delete_counter = 0
        delete_counter+=1
        cur.execute('''select * from mail_record where strftime(?,time) < ?''',("%Y-%m-%d %H:%M:%S",datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        results = cur.fetchall()
        for item in results:
            if check_ifup(item[0]):
                send_sms(item[0],item[2],item[3])
                send_email(item[0],item[1])
                update_time(item[0],(datetime.now()+timedelta(hours=cooldown_time)).strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    send_messages()
