from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms import FileField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email
from wtforms.validators import Regexp, EqualTo, ValidationError
from website.models import User



class RegistrationForm(FlaskForm):
  fname=StringField("First Name", validators=[DataRequired(), Length(min=2, max=25)])
  lname=StringField("Last Name", validators=[DataRequired(), Length(min=2, max=25)])
  email=StringField("Email", validators=[DataRequired(), Email()] )
  password=PasswordField(
      "password",
      validators=[ 
        DataRequired(),
        Regexp(
          "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_-])[A-Za-z\d@$!%*?&_-]{8,32}$"
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


class RequestResetPasswordForm(FlaskForm):
   email = StringField(validators=[DataRequired(), Email()])
   submit = SubmitField('Reset Password')
   

class ResetPasswordForm(FlaskForm):
  password=PasswordField(
      "password",
      validators=[ 
        DataRequired(),
        Regexp(
          "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_-])[A-Za-z\d@$!%*?&_-]{8,32}$"
          )
       ]
    )
  confirm_password=PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")] )
  submit=SubmitField("Reset password")