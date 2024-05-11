
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_ckeditor import CKEditor
from flask_mail import Mail
from website.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"
migrate = Migrate(db)
ckeditor = CKEditor()
mail = Mail()



def create_app(config_calss= Config):
    app = Flask(__name__)
    app.config.from_object(config_calss)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'users_bp.login'
    login_manager.login_message_category = 'info'
    migrate.init_app(app, db)
    ckeditor.init_app(app)
    mail.init_app(app)

    from website.main.routes import main
    from website.categories.routes import categories_bp
    from website.courses.routes import courses_bp
    from website.units.routes import units_bp
    from website.lessons.routes import lessons_bp
    from website.users.routes import users_bp

    app.register_blueprint(main)
    app.register_blueprint(categories_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(units_bp)
    app.register_blueprint(lessons_bp)
    app.register_blueprint(users_bp)
   

    return app


   




  













