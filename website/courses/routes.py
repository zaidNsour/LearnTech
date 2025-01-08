from os import abort
from website.models import JoinedCourse, Lesson, Course,CourseComment, Unit
from flask import render_template, url_for, flash, redirect, request
from website.courses.forms import UpdateCourseForm, CourseCommentForm
from website import db
from flask_login import current_user, login_required
from flask import get_flashed_messages
from website.helper import delete_picture, instructor_required, save_picture



from flask import Blueprint
courses_bp=Blueprint("courses_bp", __name__, url_prefix='/courses')


@courses_bp.route("/<string:course_title>",  methods=['GET', 'POST'])
def course(course_title):
    course = Course.query.filter_by(title= course_title).first_or_404() 
    related_courses= Course.query.filter_by(category= course.category).all()
    # modify this to be lesson thats user arrive to it 
    current_lesson= Lesson.query.filter_by(course_id= course.id).first()
    comments= CourseComment.query.filter_by(course_id= course.id).all()

    is_joined = False  
    if course in current_user.joined_courses:
       is_joined = True
 
    form = CourseCommentForm()
    if  form.validate_on_submit():
      new_comment = CourseComment(
      course_id= course.id,
      user= current_user,
      content= form.content.data
      ) 

      db.session.add(new_comment)
      db.session.commit() 
        # Redirect to the same page to avoid form resubmission
      return redirect( url_for('courses_bp.course', course_title= course_title) )
    
    flash_messages = get_flashed_messages()
   
    return render_template(
      "courses/course.html",
      title= course.title,
      course= course,
      related_courses= related_courses,
      current_lesson= current_lesson,
      comments= comments, 
      form= form,
      flash_messages= flash_messages,
      is_joined= is_joined
    )


@courses_bp.route("/courses")
def courses():
   page=request.args.get('page', 1, type=int)
   courses=Course.query.paginate(page= page, per_page= 6)
   return render_template("courses/courses.html", title="Courses", courses = courses)


@courses_bp.route("/update_course/<string:course_title>", methods=["POST", "GET"])
@instructor_required
def update_course(course_title):
  course=Course.query.filter_by(title=course_title).first_or_404()

  if course.author != current_user:
      abort(403)

  update_course_form = UpdateCourseForm()
  if update_course_form.validate_on_submit():
    # maybe the thing that's instructor can update it should be limited
    course.category = update_course_form.category.data
    course.title = update_course_form.title.data
    course.description = update_course_form.description.data
    course.price = update_course_form.price.data

    if update_course_form.icon_image.data:
        delete_picture(course.icon, path="static/images/course_pics")
        icon_file=save_picture(update_course_form.icon_image.data,
                               path="static/images/course_pics")
        course.icon=icon_file

    db.session.commit()
    flash("Your Course has been updated!", "success")
    return redirect(url_for("courses_bp.your_courses"))
  
  elif request.method == 'GET':
     update_course_form.category.data = course.category
     update_course_form.title.data = course.title
     update_course_form.description.data =  course.description
     update_course_form.price.data = course.price

  return render_template(
     "courses/update_course.html",
     course = course,
     update_course_form = update_course_form 

  )


@courses_bp.route("/edit_course_content/<string:course_title>", methods=["POST", "GET"])
@instructor_required
def edit_course_content(course_title): 
   course=Course.query.filter_by(title=course_title).first_or_404()
   units=Unit.query.filter_by(course=course).order_by(Unit.number).all()

   unit_lessons = {} 
   for unit in units:
      lessons = Lesson.query.filter_by(unit= unit).all()
      unit_lessons[unit.id] = lessons  # Store lessons for the unit
   
   return render_template( "courses/edit_course_content.html", 
                          title = course.title,
                          course = course,
                          units = units,
                          unit_lessons = unit_lessons
                          )



@courses_bp.route("/enroll_user/<string:course_id>", methods=["POST", "GET"])
@login_required
def enroll_user(course_id):
  
  course = Course.query.filter_by(id = course_id).first()
  if not course:
    flash("Invalid Course Id", "error")

  ex_enrollment = JoinedCourse.query.filter_by(user_id= current_user.id,course_id= course.id).first()
  if ex_enrollment:
    flash("User already inrolled to this course", "error")
    return redirect(url_for("courses_bp.courses"))

  enrollment = JoinedCourse(user_id= current_user.id,course_id= course.id)
  db.session.add(enrollment)
  db.session.commit()

  flash_messages = get_flashed_messages()
  
  return render_template(
    "courses/enroll_done.html",
    title= "Enroll done",
    flash_messages= flash_messages
    )