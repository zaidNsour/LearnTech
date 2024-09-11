import os

class Config:
  DB_NAME="database.db"
  SECRET_KEY=os.environ.get('SECRET_KEY')
  SQLALCHEMY_DATABASE_URI=f"sqlite:///{DB_NAME}"
  SQLALCHEMY_TRACK_MODIFICATIONS = True
  MAIL_SERVER='smtp.googlemail.com'
  MAIL_PORT= 587
  MAIL_USE_TLS= True
  MAIL_USERNAME= os.environ.get('EMAIL_USER')
  MAIL_PASSWORD= os.environ.get('EMAIL_PASS')
  #for security concern the Email_USER and EMAIL_PASS is stored as Environment variables 
