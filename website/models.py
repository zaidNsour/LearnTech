from flask import current_app
from datetime import datetime
from website import db, login_manager
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from itsdangerous import URLSafeTimedSerializer as Serializer



@login_manager.user_loader
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

  is_instructor=db.Column(db.Boolean, nullable=True, default=False)
  is_admin=db.Column(db.Boolean, nullable=True, default=False)
  is_super_admin=db.Column(db.Boolean, nullable=True, default=False)

  courses = db.relationship("Course", backref="author", lazy=True, cascade='all, delete-orphan')
  lesson_comments=db.relationship("LessonComment", backref="user", lazy=True, cascade='all, delete-orphan')
  course_comments=db.relationship("CourseComment", backref="user", lazy=True, cascade='all, delete-orphan')
  joined_courses = db.relationship("JoinedCourse", back_populates="user", cascade='all, delete-orphan')


  def get_reset_token(self):
      s = Serializer(current_app.config['SECRET_KEY'], salt='pw-reset')
      return s.dumps({'user_id': self.id})
    
  @staticmethod
  def verify_reset_token(token, age=3600):
    s = Serializer(current_app.config['SECRET_KEY'], salt='pw-reset')
    try:
      user_id = s.loads(token, max_age=age)['user_id']
    except:
      return None
    
    return User.query.get(user_id)
  
  def __repr__(self):
    return f"{self.fname} {self.lname}" 
  


  

class Category(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  title=db.Column(db.String(50),unique=True, nullable=False)
  icon=db.Column(db.String(20),nullable=False, default="default_icon.jpg")
  courses=db.relationship("Course", backref="category", lazy=True, cascade='all, delete-orphan')
  def __repr__(self):
    return f"category({self.title} )"
  

  
class Course(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  user_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  category_id=db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

  title=db.Column(db.String(50),unique=True, nullable=False)
  description=db.Column(db.String(150),nullable=False)
  icon=db.Column(db.String(20),nullable=False, default="default_icon.png")
  price=db.Column(db.Integer , nullable=False)

  #units = db.relationship("Unit", backref="course", lazy=True, cascade="all, delete-orphan")
  #lessons = db.relationship("Lesson", backref="course", lazy=True, cascade="all, delete-orphan")
  joined_users = db.relationship("JoinedCourse", back_populates="course", cascade='all, delete-orphan')

  def __repr__(self):
    return f"Course({self.title}, {self.price})"
  
  def __str__(self):
        return self.title  # Assuming `title` field stores the course name
  


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
    

class CourseComment(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  course_id=db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
  user_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  title=db.Column(db.String(50),nullable=False)
  details=db.Column(db.String(150),nullable=False)
  rating=db.Column(db.Integer,nullable=False)



class Unit(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  course_id=db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
  course = db.relationship('Course', backref=db.backref('units', lazy=True))
  title=db.Column(db.String(50),nullable=False)
  number=db.Column(db.Integer,nullable=False)
  #lessons = db.relationship("Lesson", backref="unit", lazy=True, cascade="all, delete-orphan")
  __table_args__ = (
     UniqueConstraint('course_id', 'title', name='unique_unit_per_course_title'),
    )
  def __repr__(self):
    return f"Unit( {self.title} )"
  
  

class Lesson(db.Model):
  id=db.Column(db.Integer, primary_key=True)

  course_id=db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
  course = db.relationship('Course', backref=db.backref('lessons', lazy=True))

  unit_id=db.Column(db.Integer, db.ForeignKey("unit.id"), nullable=False)
  unit = db.relationship('Unit', backref=db.backref('lessons', lazy=True))

  title=db.Column(db.String(50), unique=False, nullable=False)
  number=db.Column(db.Integer,nullable=False)
  course_order=db.Column(db.Integer,nullable=True)
  video_url=db.Column(db.String(300),nullable=False)
  details=db.Column(db.String(150),nullable=False)
  date=db.Column(db.DateTime, nullable=False, default=datetime.now)
  comments = db.relationship("LessonComment", backref="lesson", lazy=True, cascade='all, delete-orphan')

  def __repr__(self):
    return f"Lesson({self.title}, {self.date})"
  

class LessonComment(db.Model):
  id=db.Column(db.Integer, primary_key=True)
  lesson_id=db.Column(db.Integer, db.ForeignKey("lesson.id"), nullable=False)
  user_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  title=db.Column(db.String(50),nullable=False)
  details=db.Column(db.String(150),nullable=False)
  rating=db.Column(db.Integer,nullable=False)
  

  

 

 