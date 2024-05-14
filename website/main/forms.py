from flask_wtf import FlaskForm
from wtforms import  SearchField, SubmitField
from wtforms.validators import DataRequired, Length


class SearchForm(FlaskForm):
  query=SearchField("query", validators=[DataRequired(),Length(max= 100)])
  submit=SubmitField('Search')
