from website import admin, db, bcrypt
from website.models import User, Category, Course, JoinedCourse
from website.admins.forms import NewCourseForm, UpdateCourseForm, NewUserForm
from wtforms import PasswordField
from flask import Blueprint, flash
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_admin.form.upload import FileUploadField
from flask_login import current_user


#for logging use: print('\n\n\n msg', file=sys.stderr)


### methods ###
from website.helper import delete_picture, save_picture


admins_bp=Blueprint('admins_bp',__name__)

class MyModelView(ModelView):
  def is_accessible(self):
    #change it to current_user.is_admin but know keep it for testing
    return current_user.is_authenticated and current_user.is_admin == True

class MyAdminIndexView(AdminIndexView):
   def is_accessible(self):
    #change it to current_user.is_admin but know keep it for testing
    return current_user.is_authenticated and current_user.is_admin == True
   
   
############################## User ################################
   
class UserAdmin(MyModelView):
  #column_list = ('fname', 'lname', 'email', 'is_instructor', 'is_admin')
  #column_list = ('fname', 'lname', 'email', 'is_instructor')

  column_list = ('fname', 'lname', 'email', 'is_instructor', 'is_admin',)
  column_labels = dict(fname = 'First Name', lname = 'Last Name')
  form_excluded_columns = ('is_super_admin','password')

  form_extra_fields = {
        'file_path': FileUploadField('Profile image',
                                      base_path='/path/to/upload',
                                      allowed_extensions=['jpg', 'png']),
        'password2': PasswordField('Password')
                      }
  
  form_columns = (
    'fname',
    'lname',
    'email',
    'file_path',
    'password2',
    'is_instructor',
    'is_admin',   
    )
  
  column_searchable_list = ['fname', 'lname']
  page_size = 20

  def create_form(self, obj=None): 
    return NewUserForm()
  
  def delete_model(self, model):
    try:
      if current_user.is_super_admin:
        self.session.delete(model)
        self.session.commit()
        flash('Course was successfully deleted.', 'success')
      
    except Exception as ex:
      flash(f'Error deleting user: {str(ex)}', 'error')
      self.session.rollback()
      return False
    
    return True

  def on_model_change(self, form, model, is_created):
    try:

      if form.password2.data != '':
              model.password = bcrypt.generate_password_hash(form.password2.data).decode("utf-8")

      '''
      else:
          if not is_created:
            # Retrieve the existing password and retain it
              existing_model = self.session.query(self.model).get(model.id)
              model.password = existing_model.password
      
      '''        
      
      if form.email.data != model.email:  # Email changed
       if self.model_class.query.filter_by(email=form.email.data).first():
        flash("Email already exists!", "error")
        return False  # Prevent saving
       
      if not is_created and form.file_path.data:

        if model.img_file != 'default_image.jpg':
          delete_picture(model.img_file, path="static/images/user_pics") 

        filename = save_picture(form.file_path.data, path="static/images/user_pics")
        model.img_file = filename

      return super().on_model_change(form, model, is_created)
    
    except Exception as e:
      flash(f"An error occurred while saving the model: {str(e)}", "error")

############################## Course ################################

class CourseAdmin(MyModelView):

  column_list = ('title', 'description', 'price')
  form_excluded_columns = ('icon',)

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

      model.author= form.instructor.data

      return super().on_model_change(form, model, is_created)
    
    except Exception as e:
      flash(f"An error occurred while saving the model: {str(e)}", "error")

############################## Category ################################

class CategoryAdmin(MyModelView):
  column_list = ('title',)
  form_excluded_columns = ('icon',)

  def delete_model(self, model):
    try:
      delete_picture(model.icon, path="static/images/category_pics") 
      # Ensure the joined courses are deleted
     
      self.session.query(Category).filter_by(id= model.id).delete()
      self.session.commit()
      # Now delete the course itself
      self.session.delete(model)
      self.session.commit()

    except Exception as e:
      flash(f'Error deleting category: {str(e)}', 'error')
      self.session.rollback()
      return False
    
    return True
  
############################# Joined course #################################

class JoinedCourseAdmin(MyModelView):
  column_list = ('course.title','user.fname','user.lname' ,'user.email', 'enroll_date','course_progress' )
  column_labels = {"course.title":'Course Title','user.fname':'First Name','user.lname':'Last Name',
                   'user.email':'Email' ,'enroll_date':'Enroll Date'}
  column_searchable_list = ['course.title']
  form_excluded_columns = ('enroll_date')

 

admin.add_view( UserAdmin(User, db.session) )
admin.add_view( CategoryAdmin(Category, db.session) )
admin.add_view( CourseAdmin(Course, db.session) )
admin.add_view( JoinedCourseAdmin( JoinedCourse, db.session) )


