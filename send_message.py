import sqlite3, requests, smtplib, time, os
from datetime import datetime, timedelta
import user_credentials as UC
from constants import *

class database_operator:
    def __init__(self):
        """ TASK    :   Check if the DB file -> flush the table 
                        Form DB file -> create table schema.
                        
        """
        self.conn = sqlite3.connect(database)
        self.cur = self.conn.cursor()
        # TODO : Remove the flushing when records where you're support user data.
        # Create a New Table with  URL, EMAIL, PHONE, CARRIER, TIME_CREATE, TIME_OPERATION
        self.cur.execute(f'''drop table if exists {table}''')
        self.cur.execute(f'''CREATE TABLE {table} 
        (URL  VARCHAR NOT NULL,
        EMAIL VARCHAR NOT NULL,
        PHONE BIGINT(10) NOT NULL DEFAULT (0),
        CARRIER VARCHAR NOT NULL,
        TIME_CREATE DATE,
        TIME_OPERATION DATE);''')
        self.conn.commit()

    def add(self,args):
        """ ADDS new entry into the table.
        """
        if not all([True if i in field_verify else False for i in args.keys()]):
            return
        # URL, EMAIL, PHONE, CARRIER, TIME_CREATE, TIME_OPERATION
        time = datetime.now().strftime(time_format)
        self.cur.execute(f'''insert into {table} values({args["url"]},{args["email"]},
        {args["phone"]},{args["carrier"]},{time},{time})''')
        self.conn.commit()
    
    def read(self):
        self.cur.execute(f'''select * from {table} where strftime("%Y-%m-%d %H:%M:%S",TIME_OPERATION) < "{datetime.now().strftime(time_format)}";''')
        return self.cur.fetchall()

    def delete(self):
        self.cur.execute(f'''delete from {table} where strftime("%Y-%m-%d %H:%M:%S",TIME_CREATE) <= "{(datetime.now()-timedelta(hours=24)).strftime(time_format)}"''')
        self.conn.commit()

    def update(self,url):
        self.cur.execute(f'''update {table} set TIME_OPERATION = "{(datetime.now() + timedelta(hours=cooldown_time)).strftime(time_format)}" where url="{url}";''')
        self.conn.commit()
    
    def __del__(self):
        self.conn.close()


class smtp_operator:
    def __init__(self):
        """ TASK    :   GET SMTP LOGIN.
        """   
        self.auth = (UC.gmail_account, UC.password)
        self.server = smtplib.SMTP(UC.smtp_gmail, smtp_port)
        self.server.starttls()
        self.server.login(self.auth[0], self.auth[1])

    def send_email(self,url, email):
        """ DESC    :   send an email with the predefined format to the customer.
                        TODO : Give user the priviledge to add his own custome message.
            PARAM   :   URL for the site which has is not working.
                        email address of the user registered to the mail id.
            RETURN  :   none
        """
        #time = datetime.now().strftime("%H:%M:%S %m-%d-%Y")
        time = datetime.now()
        _time = time.strftime("%H:%M:%S %p")
        _date = time.strftime("%A %B %d, %Y")
        error_text = f"The Site {url} is not responding to the HTTP requests to the site at {_time} on {_date}. \n Please note there is a SMS sent to the registered number as well.\n The logger will resume monitoring this site again in {cooldown_time} hours. \nThanks \n-Site Failure Logger Team."
        Subject = f"{url} Not Reachable!!"
        message = (f"From: {self.auth[0]}\nTo:{email}\nSubject: {Subject}")
        message += f"\n\n{error_text}"
        self.server.sendmail(self.auth[0], [email], message)
        return None
    
    def send_sms(self, url, phone, carrier):
        """ DESC    :   Send a SMS to the phone using the SMTP protocol.
            PARAM   :   url site that can not be reached.
                        phone number registered for the site.
                        carrier the provider of the service for that number.
            RETURN  :   NONE
        """
        _time = datetime.now().strftime("%H:%M:%S %p")
        error_text = 'Site: \n{} \nNOT Working:\n\n{} '.format(url,_time)
        to_number = '{}{}{}'.format(country_code["US"],phone, carriers[carrier])
        print(f'''Sending Message to {to_number}''')
        Subject = "Site Failure Detected"
        message = (f"From: {self.auth[0]}\nTo:{to_number}\nSubject: {Subject}")
        message += f"\n\n{error_text}"

        # Send text message through SMS gateway of destination number
        self.server.sendmail(self.auth[0], [to_number], message)
        return None

carriers = {
    'att': '@mms.att.net',
    'tmobile': '@tmomail.net',
    'verizon': '@vtext.com',
    'sprint': '@page.nextel.com',
    'lyca': '@mms.us.lycamobile.com'
}


def check_ifup(url):
    """ Desc    :   Function checks if the URL is UP? by checking the 
                    return status for the request head call.
        param   :   URL
        return  :   true if site is down
                    false if site is up
    """
    return requests.head(url).status_code != 200


def send_email(url, email):
    """ DESC    :   send an email with the predefined format to the customer.
                    TODO : Give user the priviledge to add his own custome message.
        PARAM   :   URL for the site which has is not working.
                    email address of the user registered to the mail id.
        RETURN  :   none
    """
    #time = datetime.now().strftime("%H:%M:%S %m-%d-%Y")
    time = datetime.now()
    _time = time.strftime("%H:%M:%S %p")
    _date = time.strftime("%A %B %d, %Y")
    error_text = f"The Site {url} is not responding to the HTTP requests to the site at {_time} on {_date}. \n Please note there is a SMS sent to the registered number as well.\n The logger will resume monitoring this site again in {cooldown_time} hours. \nThanks \n-Site Failure Logger Team."

    auth = (UC.gmail_account, UC.password)
    Subject = f"{url} Not Reachable!!"
    message = (f"From: {auth[0]}\nTo:{email}\nSubject: {Subject}")
    message += f"\n\n{error_text}"
    server = smtplib.SMTP(UC.smtp_gmail, smtp_port)
    server.starttls()
    server.login(auth[0], auth[1])
    server.sendmail(auth[0], [email], message)
    return None


def send_sms(url, phone, carrier):
    """ DESC    :   Send a SMS to the phone using the SMTP protocol.
        PARAM   :   url site that can not be reached.
                    phone number registered for the site.
                    carrier the provider of the service for that number.
        RETURN  :   NONE
    """
    time = datetime.now()
    _time = time.strftime("%H:%M:%S %p")
    _date = time.strftime("%A %B %d, %Y")
    error_text = 'Site: \n{} \nNOT Working:\n\n{} '.format(url,_time)
    to_number = '{}{}{}'.format(country_code["US"],phone, carriers[carrier])
    print(f"sending the text to {to_number}")
    auth = (UC.gmail_account, UC.password)

    # message = MIMEMultipart("alternative")
    # message['From'] = auth[0]
    # message['To'] = to_number
    # message['Subject'] = 'Site Down'

    Subject = "Site Failure Detected"
    message = (f"From: {auth[0]}\nTo:{to_number}\nSubject: {Subject}")
    message += f"\n\n{error_text}"

    # message.attach(MIMEText(user_message,"plain"))
    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP(UC.smtp_gmail, smtp_port)
    server.starttls()
    server.login(auth[0], auth[1])

    # Send text message through SMS gateway of destination number
    server.sendmail(auth[0], [to_number], message)
    return


def update_time(url, time):
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.execute('''update mail_record set time = ? where url=?''', (time, url))
    con.commit()
    con.close()


def send_messages():
    con = sqlite3.connect(database)
    cur = con.cursor()
    delete_counter = 0
    while True:
        time.sleep(1)
        if delete_counter > 100:
            cur.execute(
                '''delete from mail_record where strftime(?,time) <= ?''',
                ("%Y-%m-%d %H:%M:%S",
                 (datetime.now() -
                  timedelta(hours=24)).strftime(time_format)))
            delete_counter = 0
        delete_counter += 1
        cur.execute('''select * from mail_record where strftime(?,time) < ?''',
                    ("%Y-%m-%d %H:%M:%S",
                     datetime.now().strftime(time_format)))
        results = cur.fetchall()
        for item in results:
            if check_ifup(item[0]):
                send_sms(item[0], item[2], item[3])
                send_email(item[0], item[1])
                update_time(item[0],
                            (datetime.now() + timedelta(hours=cooldown_time)
                             ).strftime("%Y-%m-%d %H:%M:%S"))

def main_loop():
    db = database_operator()
    em = smtp_operator()
    delete_counter = 0
    while True:
        if delete_counter > 100:
            db.delete()
            delete_counter = 0
        delete_counter += 1
        results = db.read()
        for item in results:
            if check_ifup(item[0]):
                em.send_sms(item[0], item[2], item[3])
                em.send_email(item[0], item[1])
                db.update(item[0])
    
if __name__ == "__main__":
    #send_messages()
    main_loop()
