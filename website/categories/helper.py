from website.models import Course

def CourseCountInCategory(category_id):
   courses=Course.query.filter_by(category_id=category_id).all()
   return len(courses)