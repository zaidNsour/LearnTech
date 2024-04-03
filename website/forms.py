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



def choice_query():
  return Category.query 


def choice_query2():
  return Course.query 

def choice_query3():
  return Unit.query    



class NewCourseForm(FlaskForm):
  category = QuerySelectField("Category", query_factory=choice_query, get_label="name")
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



    

class NewUnitForm(FlaskForm):
  course = QuerySelectField("Course", query_factory=choice_query2, get_label="title")
  title=StringField('Title', validators=[DataRequired(),Length(max= 100)] )
  submit=SubmitField('Add')

  def validate_title(self, field):
    existing_unit = Unit.query.filter_by(course_id=self.course.data.id, title=field.data).first()
    if existing_unit:
      raise ValidationError('A unit with this title already exists for the selected course.')




class NewLessonForm(FlaskForm):
  course = QuerySelectField("Course", query_factory=choice_query2, get_label="title")
  unit = QuerySelectField("Unit", query_factory=choice_query3, get_label="title")
  title=StringField('Title', validators=[DataRequired(),Length(max= 100)] )
  details=CKEditorField("Details", validators=[DataRequired()], render_kw={"rows" : "30"})
  video_url=StringField("Video URL", validators=[DataRequired()])
  submit=SubmitField('Add')

  def validate_title(self, field):    
    existing_lesson = Lesson.query.filter_by(course_id=self.course.data.id, title=field.data).first()
    if existing_lesson:
      raise ValidationError('A lesson with this title already exists for the selected course.')

  


    
 



  

  
  