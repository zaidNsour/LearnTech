from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length
from wtforms.validators import  ValidationError
from website.models import  Unit


### methods ###
from website.helper import choice_query_course


class NewUnitForm(FlaskForm):
  course = HiddenField("Course")
  title=StringField('Title', validators=[DataRequired(),Length(max= 100)] )
  submit=SubmitField('Add')

  def validate_title(self, title):
    if self.course.data:
      existing_unit = Unit.query.filter_by(course_id=self.course.data.id, title=title.data).first()
      if existing_unit:
        raise ValidationError('A unit with this title already exists for the selected course.')
    

class UpdateUnitForm(NewUnitForm):
    submit = SubmitField('Update')