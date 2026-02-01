import smtplib   #This is used to connect to mail server and send mails
s = smtplib.SMTP('smtp.gmail.com',587)
s.ehlo()
s.starttls()
s.login("sivajisnehith@gmail.com","xxxx xxxx xxxx xxxx")
message = """Subject: Test Mail
He is too hot
"""
s.sendmail("snehith.24bcs7081@vitapstudent.ac.in",
           "snehithsivaji@gmail.com",
           message
)
s.quit()


