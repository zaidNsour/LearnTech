from flask_wtf import FlaskForm
from wtforms import  SearchField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


class SearchForm(FlaskForm):
  query=SearchField("query", validators=[DataRequired(),Length(max= 100)])
  submit=SubmitField('Search')

class contactForm(FlaskForm): 
  name = StringField('Name', validators=[DataRequired()]) 
  email=StringField("Email", validators=[DataRequired(), Email()] )
  message=TextAreaField('Message', validators=[DataRequired()])
  submit = SubmitField("Send") 
