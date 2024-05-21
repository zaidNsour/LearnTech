from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import FileField
from wtforms import TextAreaField, RadioField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length
from wtforms.validators import Regexp, ValidationError
from website.models import Course
from flask_ckeditor import CKEditorField




###methods###
from website.helper import choice_query_category


class NewCourseForm(FlaskForm):
  category = QuerySelectField("Category", query_factory=choice_query_category, get_label="title")
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
  icon_image = FileField(
      "Upload Course icon",validators=[FileAllowed(["jpg", "png"]) ]
    )
  
  def validate_title(self, title):
    return None 
  def validate_icon_image(self, icon_image):
    return None   
  