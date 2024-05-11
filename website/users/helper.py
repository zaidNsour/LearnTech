from flask_mail import Message
from flask import url_for
from website import  mail




#use _external because redirect from email to this route 
def send_reset_email(user):    
   token= user.get_reset_token()
   #change email
   msg=Message('Password reset request', sender= 'zaidnsour1223@gmail.com',
               recipients= [user.email],
               body=f''' To reset your password, visit the following link:
               {url_for('users_bp.reset_password', token=token, _external=True)}  
                if you did not make this request, please ignore this email'''
              )
   mail.send(msg)
   

   