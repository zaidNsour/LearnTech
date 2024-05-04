
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
from flask_mail import Mail


def create_database(app):
 if not path.exists("website/" + DB_NAME):
  with app.app_context():
    db.create_all()
  print("Created Database!")

db=SQLAlchemy()
DB_NAME="database.db"

app=Flask(__name__)
app.config["SECRET_KEY"]="aaa123456789"
app.config["SQLALCHEMY_DATABASE_URI"]=f"sqlite:///{DB_NAME}"
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT']= 587
app.config['MAIL_USE_TLS']= True
app.config['MAIL_USERNAME']= os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD']= os.environ.get('EMAIL_PASS')
#for security concern the Email_USER and EMAIL_PASS is stored as Environment variables 


app.app_context().push()

db.init_app(app)
create_database(app) 
bcrypt=Bcrypt(app)
migrate=Migrate(app, db)
ckeditor=CKEditor(app)
mail=Mail(app)

loginManager=LoginManager(app)
loginManager.login_view='login'
loginManager.login_message_category='info'

from website.routes import routes
app.register_blueprint(routes, url_prefix="/")


  













