import smtplib

server = smtplib.SMTP('127.0.0.1', 8025)


fromEmail = "admin@warwickcybersoc.com"
toEmail = "1337@warwickcybersoc.com"

subject = "Test Email"

#msg = "Hello, this is a test email from the Warwick Cyber Security Society."
msg = '{{ 7*7 }}'

message = 'Subject: {}\n\n{}'.format(subject, msg)

server.sendmail(fromEmail, toEmail, message)

server.quit()

