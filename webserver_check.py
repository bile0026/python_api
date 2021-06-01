import requests
import json
from configparser import ConfigParser
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    config = ConfigParser()
    config.read("webserver.ini")
    webserver_config = config['WebServer']
except:
    print("Error: there is something wrong with your .ini file")

if webserver_config['ssl_verify'] == 'True':
    webserver_url = 'https://' + webserver_config['web_server']
else:
    webserver_url = 'http://' + webserver_config['web_server']

# try:
if webserver_config['ssl_verify'] != 'True':
    result = requests.get(webserver_url, verify=False)
    # print(result.status_code)
else:
    result = requests.get(webserver_url)

if result.status_code == 200:
    print("Webserver " +
          webserver_config['web_server'] + " seems to be working...")
    print("Status code:", result.status_code)
    exit
else:
    print("Problem with " + webserver_config['web_server'] + "...")
    print("Status code:", result.status_code)
    # Build email Metadata
    message = MIMEMultipart('alternative')
    message['Subject'] = "New " + webserver_config['web_server'] + " Alert"
    message['From'] = webserver_config['from_email_address']
    message['To'] = webserver_config['to_email_address']
    message.attach(MIMEText(result.text, "html"))
    # Send the email
    with smtplib.SMTP(webserver_config['smtp_server'], 25) as server:
        server.sendmail(webserver_config['from_email_address'],
                        webserver_config['to_email_address'], message.as_string())
# except ConnectionError:
#     print("Error: connection error")
# except OSError:
#     print("Error: problem with certificate")
# except:
#     print("Error: Problem connecting to web server")
