from flask import Blueprint
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from website import admin, db, bcrypt
from website.models import User, Category, Course, Unit, Lesson, JoinedCourse
from flask_login import current_user

admins_bp=Blueprint('admins_bp',__name__)

class MyModelView(ModelView):
  def is_accessible(self):
    #change it to current_user.is_admin but know keep it for testing
    return current_user.is_authenticated and current_user.id == 1

class MyAdminIndexView(AdminIndexView):
   def is_accessible(self):
    #change it to current_user.is_admin but know keep it for testing
    return current_user.is_authenticated and current_user.id == 1
   
class UserModelView(ModelView):
  def on_model_change(self, form, model, is_created):
    model.password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

  def is_accessible(self):
    #change it to current_user.is_admin but know keep it for testing
    return current_user.is_authenticated and current_user.id == 1


admin.add_view( UserModelView(User, db.session) )
admin.add_view( MyModelView(Category, db.session) )
admin.add_view( MyModelView(Course, db.session) )
admin.add_view( MyModelView( Unit, db.session) )
admin.add_view( MyModelView( Lesson, db.session) )
admin.add_view( MyModelView(JoinedCourse, db.session) )

