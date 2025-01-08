from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email



# may be email should not allowed to update
class UpdateProfileForm(FlaskForm):
  email= StringField("Email", validators=[DataRequired(), Email()] )
  bio= TextAreaField("Bio")
  image = FileField(
      "Update Profile Picture", validators=[FileAllowed(["jpg", "png"])]
    )
  submit=SubmitField("Update")