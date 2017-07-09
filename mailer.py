#Email Libraries
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


"""TODO: Generate Email Server Account"""
EMAIL = None

try:
	password = os.environ["PASSWORD"]
except:
	print("Mail Server is offline. Please load password to continue...")


def send_mail(email,subject,text):
	#Generate Message
	msg = MIMEMultipart()
	msg['From'] = "InternCorner@PasswordReset"
	msg["To"] = email
	msg["Subject"] = subject
	body = "Hi from the Intern Corner Team! \n"
	body += "You recently requested a password reset" \
			"Here is your verification code: \n"
	body += text

	#Edit this attribute for richer email text
	msg.attach(MIMEText(body,'plain'))

	#Issue server connection
	server = smtplib.SMTP('smtp.gmail.com',587)
	server.starttls()
	server.login(EMAIL,password)
	text = msg.as_string()
	server.sendmail("InternCorner@PasswordReset",
					email,text)
	server.quit()




