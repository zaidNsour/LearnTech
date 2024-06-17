from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms import FileField
from wtforms import TextAreaField, RadioField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, Optional
from wtforms.validators import Regexp, ValidationError, EqualTo
from website.models import Course, Lesson, Unit
from website.models import User
from flask_ckeditor import CKEditorField



###methods###
from website.helper import choice_query_category
from website.admins.helper import choice_query_instructor


############################## Course ################################

class NewCourseForm(FlaskForm):
  category = QuerySelectField("Category", query_factory=choice_query_category, get_label="title")
  instructor = QuerySelectField("Instructor", query_factory=choice_query_instructor, get_label="email")
  title=StringField('Title', validators=[DataRequired(),Length(max= 100)] )
  description=CKEditorField("Description", validators=[DataRequired()], render_kw={"rows" : "30"} )
  price=StringField('Price',validators=[DataRequired(),Length(max= 10),Regexp('^\d+$') ] )
  icon_image = FileField(
      "Upload Course icon", validators=[FileAllowed(["jpg", "png"]) ]
    )


  def validate_title(self, title):
    course=Course.query.filter_by(title= title.data).first()
    if course:
      raise ValidationError("Course Title is already exist")
    
  def validate_icon_image(self, icon_image):
        if not icon_image.data:
            raise ValidationError("Please upload an icon for the course")
        

  
class UpdateCourseForm(NewCourseForm):
 
  def validate_title(self, title):
    return None 
  def validate_icon_image(self, icon_image):
    return None   
  
############################## User ################################

class NewUserForm(FlaskForm):
  fname = StringField("First Name", validators=[DataRequired(), Length(min=2, max=25)])
  lname = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=25)])
  email = StringField("Email", validators=[DataRequired(), Email()] )
  password2 = PasswordField(
      "password",
      validators=[ 
        DataRequired(),
        Regexp(
          "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_-])[A-Za-z\d@$!%*?&_-]{8,32}$"
          )
       ]
    )
  is_instructor = BooleanField("Is Instructor")
  is_admin = BooleanField("Is Admin")

  def validate_email(self, email):
    user=User.query.filter_by(email= email.data).first()
    if user:
      raise ValidationError("Email is already exist")
    


class  UpdateUserForm(FlaskForm):
  fname = StringField("First Name", validators=[DataRequired(), Length(min=2, max=25)])
  lname = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=25)])
  email=StringField("Email", validators=[DataRequired(), Email()] )
  password = PasswordField("password",validators=[Optional()] )
  bio=TextAreaField("Bio", validators=[Optional()])
  img_file = FileField("Update Profile Picture", validators=[ FileAllowed(["jpg", "png"]) ,Optional()]  )
  is_instructor = BooleanField("Is Instructor")
  is_admin = BooleanField("Is Admin")

############################# joined course #################################
