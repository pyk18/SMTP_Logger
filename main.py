import smtplib, sqlite3, sys, requests
from flask import Flask, request, render_template
from user_credentials import *
from constants import *
from datetime import datetime,timedelta


DEBUG = True
app = Flask(__name__)
app.config["TEMPLATE_AUTO_RELOAD"] = True


def add_into_table(url, email, phone, carrier):
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.execute("insert into mail_record values(?,?,?,?,?,?)",
                (url, email, phone, carrier,
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S'),datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    con.commit()
    con.close()
    return


@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
        url = request.form['site']
        # time = request.form['time']
        email = request.form['email']
        phone = request.form['phone']
        carrier = request.form['carrier']
        add_into_table(url, email, phone, carrier)
        return render_template(
            'thanks.html',
            time=(datetime.now() +
                  timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"))

    if request.method == "GET":
        return render_template('index.html')


if __name__ == "__main__":

    app.run(debug=True)