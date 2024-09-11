from website.models import  Lesson, Unit, Course
from website import db
from sqlalchemy import func


def choice_query_unit(course_title):
  course = Course.query.filter_by(title = course_title).first()
  if course:
    return Unit.query.filter_by(course_id=course.id).all()
  else:
    return []  



def choice_query_test(form):
  """
  This function dynamically filters units based on the selected course.
  """
  course = form.course.data  # Assuming 'course' field holds the ID
  
  if course:
    return Unit.query.filter_by(course_id=course.id).all()
  else:
    return []  # Return an empty list if no course is selected
  
def getMaxNumberInLesson(course_id):
  return db.session.query(func.max(Lesson.number)).filter_by(course_id=course_id).scalar() or 0


def get_previous_next_lesson(lesson):
  if lesson:
    
    course = lesson.course 
    number=lesson.number

    lesson_count = Lesson.query.filter_by(course=course).count()

    # Calculate the previous and next lesson numbers
    previous_number = number - 1 if number > 1 else None
    next_number = number + 1 if number < lesson_count else None

    # Query the previous and next lessons based on the calculated numbers
    previous_lesson = Lesson.query.filter_by(course_id=course.id, number=previous_number).first() if previous_number else None
    next_lesson = Lesson.query.filter_by(course_id=course.id, number=next_number).first() if next_number else None
                       
    return previous_lesson, next_lesson
  else:
     return None , None
  