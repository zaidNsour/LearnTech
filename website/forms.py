from typing import Self
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField, BooleanField, TextAreaField
from wtforms import FileField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email
from wtforms.validators import Regexp, EqualTo, ValidationError
from website.models import User, Course, Category, Unit, Lesson
from flask_login import current_user
from flask_ckeditor import CKEditorField
from flask import request
from functools import partial



class RegistrationForm(FlaskForm):
  fname=StringField("First Name", validators=[DataRequired(), Length(min=2, max=25)])
  lname=StringField("Last Name", validators=[DataRequired(), Length(min=2, max=25)])
  email=StringField("Email", validators=[DataRequired(), Email()] )
  password=PasswordField(
      "password",
      validators=[ 
        DataRequired(),
        Regexp(
          "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,32}$"
          )
       ]
    )
  confirm_password=PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")] )
  submit=SubmitField("Sign Up")



  def validate_email(self, email):
    user=User.query.filter_by(email= email.data).first()
    if user:
      raise ValidationError("Email is already exist")
    
  


class LoginForm(FlaskForm):
  email=StringField("Email", validators=[DataRequired(), Email()] )
  password=PasswordField("Password", validators=[DataRequired()])
  remember=BooleanField("Remember Me")
  submit=SubmitField("Login")



class  UpdateProfileForm(FlaskForm):
  email=StringField("Email", validators=[DataRequired(), Email()] )
  bio=TextAreaField("Bio")
  picture = FileField(
      "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
  submit=SubmitField("Update")


   
class NewCategoryForm(FlaskForm):
  title=StringField('Title', validators=[DataRequired(),Length(max= 100)] )
  icon_image = FileField(
    "Upload Category icon", validators=[ FileAllowed(["jpg", "png"]) ]
    )
  submit=SubmitField('Add')

  def validate_title(self, title):
    category=Category.query.filter_by(title= title.data).first()
    if category:
      raise ValidationError("Category Title is already exist")
    
  def validate_icon_image(self, icon_image):
        if not icon_image.data:
            raise ValidationError("Please upload an icon for the category")



def choice_query_category():
  return Category.query 


def choice_query_course():
  return Course.query 




class NewCourseForm(FlaskForm):
  category = QuerySelectField("Category", query_factory=choice_query_category, get_label="title")
  title=StringField('Title', validators=[DataRequired(),Length(max= 100)] )
  description=CKEditorField("Description", validators=[DataRequired()], render_kw={"rows" : "30"} )
  price=StringField('Price',validators=[DataRequired(),Length(max= 10),Regexp('^\d+$') ] )
  icon_image = FileField(
      "Upload Course icon", validators=[FileAllowed(["jpg", "png"]) ]
    )
  submit=SubmitField('Add')

  def validate_title(self, title):
    course=Course.query.filter_by(title= title.data).first()
    if course:
      raise ValidationError("Course Title is already exist")
    
  def validate_icon_image(self, icon_image):
        if not icon_image.data:
            raise ValidationError("Please upload an icon for the course")
        


class NewUnitForm(FlaskForm):
  course = QuerySelectField("Course", query_factory=choice_query_course, get_label="title")
  title=StringField('Title', validators=[DataRequired(),Length(max= 100)] )
  submit=SubmitField('Add')

  def validate_title(self, field):
    existing_unit = Unit.query.filter_by(course_id=self.course.data.id, title=field.data).first()
    if existing_unit:
      raise ValidationError('A unit with this title already exists for the selected course.')
    
 

def choice_query_test():
      return Unit.query.filter_by(course_id=1)


class NewLessonForm(FlaskForm):
    course = QuerySelectField("Course", query_factory=choice_query_course, get_label="title")

   

    unit = QuerySelectField("Unit", query_factory=choice_query_test, get_label="title")
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    details = CKEditorField("Details", validators=[DataRequired()], render_kw={"rows": "30"})
    video_url = StringField("Video URL", validators=[DataRequired()])
    submit = SubmitField('Add')

    
    def validate_title(self, field):
        if self.course.data and self.course.data.id is not None:
            existing_lesson = Lesson.query.filter_by(course_id=self.course.data.id, title=field.data).first()
            if existing_lesson:
                raise ValidationError('A lesson with this title already exists for the selected course.')


  


    
 



  

  
  