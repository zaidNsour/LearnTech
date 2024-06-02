from flask_mail import Message
import os
from flask import flash, url_for

import smtplib
from email.message import EmailMessage
from website import mail



def send_contact_us_email(name, email, message):    
   msg=Message(subject='Contuct us request',
               sender= os.environ.get('EMAIL_USER'),
               recipients= [os.environ.get('EMAIL_USER')],
               body=
            f'''
                New Message Received!
                Name:{name}
                Email: {email}
                Message:
    
                    {message}
                
                '''
              )
   mail.send(msg)





'''

def send_contact_us_email(name, email, message):
    msg = EmailMessage()
    msg['Subject'] = 'Contact Us Request'
    msg['From'] = 'Your Name <zaidnsour1223@gmail.com>'  # Replace with your actual email address
    msg['To'] = 'Recipient Name <zaidnsour1223@gmail.com>'  # Replace with the email address you want to receive messages

    # Create HTML content with proper indentation and formatting
    html_content = f"""
    <h2>New Message Received!</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Message:</strong></p>
    <blockquote>
        {message}
    </blockquote>
    """
    msg.add_alternative(html_content, subtype='html')

    # Configure SMTP server details (replace with your own)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:  # Use SSL for secure connection
        server.login(os.environ.get('EMAIL_USER'), os.environ.get('EMAIL_PASS'))  # Replace with your email and password
        server.send_message(msg)

    flash('The message has been sent successfully!', 'success')


'''
