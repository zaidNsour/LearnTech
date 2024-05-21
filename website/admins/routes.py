from __future__ import print_function # In python 2.7
import sys
from flask import Blueprint, flash
from website import admin, db, bcrypt
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from website.models import User, Category, Course, Unit, Lesson, JoinedCourse
from flask_login import current_user
from website.admins.forms import NewCourseForm, UpdateCourseForm

#for logging use: print('\n\n\n msg', file=sys.stderr)



### methods ###
from website.helper import delete_picture, save_picture
from website.courses.helper import getAverageReviewFromComments



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
  

  
class CourseAdmin(ModelView):



  def delete_model(self, model):
    try:
      delete_picture(model.icon, path="static/images/course_pics") 
      # Ensure the joined courses are deleted
      self.session.query(JoinedCourse).filter_by(course_id=model.id).delete()
      self.session.commit()
      # Now delete the course itself
      self.session.delete(model)
      self.session.commit()
      flash('Course was successfully deleted.', 'success')

    except Exception as e:
      flash(f'Error deleting course: {str(e)}', 'error')
      self.session.rollback()
      return False
    
    return True

  
  def create_form(self, obj=None):
    form = NewCourseForm()
    return  form 
    
    
  def edit_form(self, obj=None):
      form = UpdateCourseForm()
      return form
  

  def on_form_prefill(self, form, id):
    try:
      model = self.get_one(id)
      if model:
        form.category.data = model.category
        form.title.data = model.title
        form.description.data = model.description
        form.price.data = model.price  
      else:
        flash(f"Record with ID {id} not found.", "error")

    except Exception as e:
      flash(f"An error occurred while pre-filling the form: {str(e)}", "error")
        
  
  
  def on_model_change(self, form, model, is_created):
    try:
      if not is_created:

        if form.icon_image.data:
          delete_picture(model.icon, path="static/images/course_pics") 

      if form.icon_image.data:
        icon_file=save_picture(form.icon_image.data,
                               path="static/images/course_pics")
        model.icon = icon_file

      model.author= current_user

      return super().on_model_change(form, model, is_created)
    
    except Exception as e:
      flash(f"An error occurred while saving the model: {str(e)}", "error")

  

admin.add_view( UserModelView(User, db.session) )
admin.add_view( MyModelView(Category, db.session) )
admin.add_view( CourseAdmin(Course, db.session) )
admin.add_view( MyModelView( Unit, db.session) )
admin.add_view( MyModelView( Lesson, db.session) )
admin.add_view( MyModelView(JoinedCourse, db.session) )

