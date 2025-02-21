
import smtplib
from email.message import EmailMessage

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_FROM = "csc3028.evil.banking.system"
EMAIL_PASSWORD = "jvuyfavjtlhmxzuh"  # Use app password if 2FA is enabled
# jvuy favj tlhm xzuh
EMAIL_TO = "danielwilson500219@gmail.com"

msg = EmailMessage()
msg.set_content("Test email")
msg['Subject'] = 'Test'
msg['From'] = EMAIL_FROM
msg['To'] = EMAIL_TO

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=60) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        #server.send_message(msg)
        server.sendmail(EMAIL_FROM,EMAIL_TO,'TEST')
    print("Test email sent successfully.")
except smtplib.SMTPException as e:
    print(f"Failed to send email: {str(e)}")
except Exception as ex:
    print(f"Unexpected error: {str(ex)}")


'''
import smtplib
# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 465, timeout=60)
# start TLS for security
#s.starttls()
# Authentication
s.login("csc3028.evil.banking.system", "jvuyfavjtlhmxzuh")
# message to be sent
message = "Test Success!"
# sending the mail
s.sendmail("csc3028.evil.banking.system", "danielwilson500219@gmail.com", message)
# terminating the session
s.quit()
'''