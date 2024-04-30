from datetime import datetime
from website import db, loginManager, app
from flask_login import UserMixin
from sqlalchemy import func
from sqlalchemy import UniqueConstraint
from itsdangerous import URLSafeTimedSerializer as serializer


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
  courses=db.relationship("Course", backref="author", lazy=True)
  lesson_comments=db.relationship("LessonComment", backref="user", lazy=True)

  joining_course=db.relationship("Course", secondary="joined_course",
                                 backref="students", lazy=True)
  

  def get_reset_token(self):
    s= serializer(app.config['SECRET_KEY'], salt = 'pw_reset')
    return s.dumps({'user_id':self.id})
  
  @staticmethod
  def varify_reset_token(token, age= 3600):
    s = serializer(app.config['SECRET_KEY'], salt = 'pw_reset')
    try:
      user_id= s.loads(token, max_age = age)['user_id']
    except:
      return None
    return User.query.get(user_id)
  
  def __repr__(self):
    return f"User({self.fname}, {self.lname}, {self.email},{self.img_file} )"
  


class Category(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  title=db.Column(db.String(50),unique=True, nullable=False)
  icon=db.Column(db.String(20),nullable=False, default="default_icon.jpg")
  courses=db.relationship("Course", backref="category", lazy=True)
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
  units = db.relationship("Unit", backref="course", lazy=True, cascade="all, delete")
  lessons = db.relationship("Lesson", backref="course", lazy=True, cascade="all, delete")
  enrolled_users = db.relationship('User', secondary="joined_course", backref='enrolled_courses', cascade='all, delete')


  def __repr__(self):
    return f"Course({self.title}, {self.price})"
  


class JoinedCourse(db.Model):
    __tablename__ = 'joined_course'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    enroll_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    course_progress = db.Column(db.Integer, nullable=True)

    user = db.relationship('User', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')

    def __repr__(self):
        return f"JoinedCourse(user_id={self.user_id}, course_id={self.course_id})"



class Unit(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  course_id=db.Column(db.Integer, db.ForeignKey("course.id"))
  title=db.Column(db.String(50),nullable=False)
  number=db.Column(db.Integer,nullable=False)
  lessons = db.relationship("Lesson", backref="unit", lazy=True)
  __table_args__ = (
     UniqueConstraint('course_id', 'title', name='unique_unit_per_course_title'),
    )
  def __repr__(self):
    return f"category( {self.title} )"
  
  

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
  comments = db.relationship("LessonComment", backref="lesson", lazy=True)

  def __repr__(self):
    return f"Lesson({self.title}, {self.date})"
  

class LessonComment(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  lesson_id=db.Column(db.Integer, db.ForeignKey("lesson.id"))
  user_id=db.Column(db.Integer, db.ForeignKey("user.id"))
  title=db.Column(db.String(50),nullable=False)
  details=db.Column(db.String(150),nullable=False)
  rating=db.Column(db.Integer,nullable=False)
  

  

 

 