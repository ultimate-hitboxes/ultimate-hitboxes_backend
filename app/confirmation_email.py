import smtplib, ssl
import os
import math
import random

def send_confirmation_email(receiver_email, confirmation_code, username):
    message=f'Hello {username},\n\n\
Your account on Ultimate-Hitboxes was successfully created. Use the below code to activate your account.\n\n\
{confirmation_code}\n\n\
Note: this code will remain active for 24 hours'
 
    context = ssl.create_default_context()
    port=465
    sender_email="ultimatehitboxes@gmail.com"
    password=os.environ.get("EMAIL_PW")
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

def generate_confirmation_code():
    string = '0123456789'
    confirmation_code = ""
    length = len(string)
    for i in range(6) :
        confirmation_code += string[math.floor(random.random() * length)]
 
    return confirmation_code