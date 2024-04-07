from datetime import datetime
from website import db, loginManager
from flask_login import UserMixin
from sqlalchemy import func
from sqlalchemy import UniqueConstraint

@loginManager.user_loader
def load_user(user_id):
  return User.query.get( int(user_id) )



class User(db.Model, UserMixin):
  id=db.Column(db.Integer, primary_key=True)
  fname=db.Column(db.String(25),nullable=False)
  lname=db.Column(db.String(25),nullable=False)
  email=db.Column(db.String(125), unique=True, nullable=False)
  img_file=db.Column(db.String(20), nullable=False, default="default_image.jpg")
  password=db.Column(db.String(60), nullable=False)
  bio=db.Column(db.Text, nullable=True)
  is_instructor=db.Column(db.Boolean, nullable=True)
  is_admin=db.Column(db.Boolean, nullable=True)
  course=db.relationship("Course", backref="author", lazy=True)
  def __repr__(self):
    return f"User({self.fname}, {self.lname}, {self.email},{self.img_file} )"
  


class Category(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  title=db.Column(db.String(50),unique=True, nullable=False)
  icon=db.Column(db.String(20),nullable=False, default="default_icon.jpg")
  course=db.relationship("Course", backref="category_name", lazy=True)
  def __repr__(self):
    return f"category({self.title} )"
  

  
class Course(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  user_id=db.Column(db.Integer, db.ForeignKey("user.id"))
  category_id=db.Column(db.Integer, db.ForeignKey("category.id"))
  title=db.Column(db.String(50),unique=True, nullable=False)
  description=db.Column(db.String(150),nullable=False)
  icon=db.Column(db.String(20),nullable=False, default="default_icon.png")
  price=db.Column(db.Integer , nullable=False)
  unit=db.relationship("Unit", backref="course_name", lazy=True)
  Lesson=db.relationship("Lesson", backref="course_name", lazy=True)

  def __repr__(self):
    return f"Course({self.title}, {self.price})"
  



class Unit(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  course_id=db.Column(db.Integer, db.ForeignKey("course.id"))
  title=db.Column(db.String(50),nullable=False)
  number=db.Column(db.Integer,nullable=False)
  lesson=db.relationship("Lesson", backref="unit_name", lazy=True)
  __table_args__ = (
     UniqueConstraint('course_id', 'title', name='unique_unit_per_course_title'),
    )


  def __repr__(self):
    return f"category( {self.title}  )"
  
  def __init__(self, *args, **kwargs):
    super(Unit, self).__init__(*args, **kwargs)
    if self.number is None:
      # Get the maximum number for this course and add 1 to it
      max_number = db.session.query(func.max(Unit.number)).filter_by(
      course_id=self.course_id).scalar() or 0
      self.number = max_number + 1



class Lesson(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  course_id=db.Column(db.Integer, db.ForeignKey("course.id"))
  unit_id=db.Column(db.Integer, db.ForeignKey("unit.id"))
  title=db.Column(db.String(50), unique=False, nullable=False)
  number=db.Column(db.Integer,nullable=False)
  course_order=db.Column(db.Integer,nullable=True)
  video_url=db.Column(db.String(300),nullable=False)
  details=db.Column(db.String(150),nullable=False)
  date=db.Column(db.DateTime, nullable=False, default=datetime.now)
  __table_args__ = (
      UniqueConstraint('course_id', 'unit_id', 'number', name='unique_lesson_per_course_unit_number'),
    )

  def __repr__(self):
    return f"Lesson({self.title}, {self.date})"

  def __init__(self, *args, **kwargs):
    super(Lesson, self).__init__(*args, **kwargs)
    if self.number is None:
      # Get the maximum number for this course and add 1 to it
      max_number = db.session.query(func.max(Lesson.number)).filter_by(
      course_id=self.course_id).scalar() or 0
      self.number = max_number + 1

 

 