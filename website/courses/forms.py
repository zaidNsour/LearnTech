from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import FileField
from wtforms import TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length
from wtforms.validators import Regexp
from flask_ckeditor import CKEditorField
from website.helper import choice_query_category

  

class UpdateCourseForm():
  category = QuerySelectField("Category", query_factory=choice_query_category, get_label="title")
  title=StringField('Title', validators=[DataRequired(),Length(max= 100)] )
  description=CKEditorField("Description", validators=[DataRequired()], render_kw={"rows" : "30"} )
  price=StringField('Price',validators=[DataRequired(),Length(max= 10),Regexp('^\d+$') ] )
  icon_image = FileField(
      "Upload Course icon",validators=[FileAllowed(["jpg", "png"]) ]
    )
  submit=SubmitField('Update')
  
 
  
class CourseCommentForm(FlaskForm):
  content = TextAreaField('Content', validators=[DataRequired(), Length(max=150)])
  submit = SubmitField('Submit')