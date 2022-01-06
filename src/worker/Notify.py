import json
import pathlib
import datetime
import smtplib, ssl, email

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os

PRIMEMOVER_PATH = str(pathlib.Path(__file__).parent.parent.absolute())

SMTP_SERVER = "smtp.mail.yahoo.com"

SMTP_USER = "primemover_py@yahoo.com"

PORT = 465
SMTP_MAIL_FROM = "primemover_py@yahoo.com"

RECEIVER_EMAIL = "johannesl@me.com"


# Try to log in to server and send email
def send_update(password, email_list, date=datetime.date.today()):
    """

    """
    subject = "PY's Daily Update"

    body = """This is a daily update.\n\n Best regards,\nPrimemover_py\n\n"""

    message = MIMEMultipart()
    message["From"] = SMTP_MAIL_FROM

    message["Subject"] = subject

    with open(
            PRIMEMOVER_PATH + f'/resources/log/log_{date.isoformat()}.json') as f:
        log = json.load(f)
    try:
        [log['Summary ALL'].pop(k, None) for k in ['failed_status', 'failed_ids',
                                               'failed_tasks']]
    except:
        log["Tasks"]["Summary ALL"] = 'failure'
    try:
        [log['Summary neutral search'].pop(k, None) for k in
         ['failed_status', 'failed_ids',
          'failed_tasks']]
    except:
        log["Tasks"]["Summary neutral search"] = 'failure'
    body += json.dumps(log, indent='  ')

    message.attach(MIMEText(body, "plain"))
    mistakes_csv_path = PRIMEMOVER_PATH + f'/resources/log/calc_errors_log_{date.isoformat()}.csv'
    if os.path.exists(mistakes_csv_path):
        with open(mistakes_csv_path, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part_1 = MIMEBase("application", "octet-stream")
            part_1.set_payload(attachment.read())
        encoders.encode_base64(part_1)
        part_1.add_header(
            "Content-Disposition",
            f"attachment; filename= calculation_errors.csv",
        )
        message.attach(part_1)

    runner_errors_path = PRIMEMOVER_PATH + f'/resources/log/issues_log_{date.isoformat()}.csv'
    if os.path.exists(runner_errors_path):
        with open(runner_errors_path, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part_2 = MIMEBase("application", "octet-stream")
            part_2.set_payload(attachment.read())
        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part_2)
        part_2.add_header(
            "Content-Disposition",
            f"attachment; filename= runner_errors.csv",
        )
        message.attach(part_2)

    # Add header as key/value pair to attachment part

    # Create a secure SSL context
    context = ssl.create_default_context()
    for receiver_email in email_list:
        message["To"] = receiver_email
        text = message.as_string()
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
                server.login(SMTP_USER, password)
                server.sendmail(SMTP_USER, receiver_email, text)
        except Exception as e:
            # Print any error messages to stdout
            print('I did end up here!')
            print(e)


if __name__ == "__main__":

    p = input('your password here')

    send_update(p, ['johannesl@me.com', 'ulrich.matter@unisg.ch'], date=datetime.datetime.fromisoformat("2021-07-06").date())
