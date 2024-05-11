from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length
from wtforms.validators import  ValidationError
from website.models import  Category


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