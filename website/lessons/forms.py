from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms import TextAreaField, RadioField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length
from wtforms.validators import  ValidationError
from website.models import  Course, Lesson
from flask_ckeditor import CKEditorField

###methods###
from website.helper import choice_query_course 


'''
class NewLessonForm(FlaskForm):
    course = QuerySelectField("Course", query_factory=choice_query_course, get_label="title")
    unit = QuerySelectField("Unit", get_label="title")
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    details = CKEditorField("Details", validators=[DataRequired()], render_kw={"rows": "30"})
    video_url = StringField("Video URL", validators=[DataRequired()])
    submit = SubmitField('Add')
    
    def validate_title(self, title):
        if self.course.data is not None:
            existing_lesson = Lesson.query.filter_by(course_id=self.course.data.id, title=title.data).first()
            if existing_lesson:
                raise ValidationError('A lesson with this title already exists for the selected course.')

'''


class NewLessonForm(FlaskForm):
    
    unit = QuerySelectField("Unit", get_label="title")
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    details = CKEditorField("Details", validators=[DataRequired()], render_kw={"rows": "30"})
    video_url = StringField("Video URL", validators=[DataRequired()])
    submit = SubmitField('Add')
    


    def validate_title(self, title):
      if self.unit.data is not None:
        course = Course.query.filter_by(id = self.unit.data.course_id).first()
        existing_lesson = Lesson.query.filter_by(course_id=course.id, title=title.data).first()
        if existing_lesson:
           raise ValidationError('A lesson with this title already exists for the selected course.')
               
                         


class UpdateLessonForm(FlaskForm):
    course = HiddenField('course')
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    details = CKEditorField("Details", validators=[DataRequired()], render_kw={"rows": "30"})
    video_url = StringField("Video URL", validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_title(self, title):
        if self.course.data:
            existing_lesson = Lesson.query.filter_by(course_id=self.course.data.id, title=title.data).first()
            if existing_lesson:
                raise ValidationError('A lesson with this title already exists for the selected course.')
    
  
		

class NewLessonCommentForm(FlaskForm):
  title = StringField('Title', validators=[DataRequired(), Length(max=100)])
  details = TextAreaField('Details', validators=[DataRequired(), Length(max=150)])
  rating = RadioField('Rating', choices=[('5', 'Awesome - 5 stars'),
                                           
                                           ('4', 'Pretty good - 4 stars'),
                                          
                                           ('3', 'Meh - 3 stars'),
                                          
                                           ('2', 'Kinda bad - 2 stars'),
                                         
                                           ('1', 'bad - 1 star'),
                                        ],
                        validators=[DataRequired()])
  submit = SubmitField('Submit')