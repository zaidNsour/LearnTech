from os import abort
from website.models import Lesson, Course, Category, CourseComment, Unit
from flask import render_template, url_for, flash, redirect, request
from website.courses.forms import NewCourseForm, UpdateCourseForm, CourseCommentForm
from website import db
from flask_login import (
    login_required,
    current_user,
    login_required,
)
from flask import get_flashed_messages
import math


### methods ###
from website.helper import delete_picture, save_picture
from website.courses.helper import getAverageReviewFromComments


from flask import Blueprint
courses_bp=Blueprint("courses_bp", __name__)


@courses_bp.route("/<string:course_title>",  methods=['GET', 'POST'])
def course(course_title):
    course = Course.query.filter_by(title=course_title).first_or_404() 
    related_courses=Course.query.filter_by(category=course.category).all()
    #lesson thats user arrive to it 
    current_lesson=Lesson.query.filter_by(course_id= course.id).first()
    comments=CourseComment.query.filter_by(course_id=course.id).all()
    reviews_count=[0] * 5

    for comment in  comments:
       reviews_count[ comment.rating - 1 ] += 1

    avg_review= getAverageReviewFromComments(comments)
    avg_review_floor=math.floor(avg_review)  


    is_joined = False

    for joined in current_user.joined_courses:
       if course.id == joined.course_id:
          is_joined = True
          break


    form = CourseCommentForm()
    if request.method == 'POST' and form.validate_on_submit():
      new_comment = CourseComment(
      course_id=course.id,
      user=current_user,
      title=form.title.data,
      details=form.details.data,
      rating=form.rating.data
      ) 
      db.session.add(new_comment)
      db.session.commit() 
        # Redirect to the same page to avoid form resubmission
      return redirect( url_for('courses_bp.course', course_title= course_title) )
    
    flash_messages = get_flashed_messages()
   
    return render_template(
      "course.html",
      title= course.title,
      course= course,
      related_courses= related_courses,
      current_lesson= current_lesson,
      comments= comments, 
      form= form,
      reviews_count=  reviews_count,
      avg_review=  avg_review,
      avg_review_floor= avg_review_floor,
      flash_messages= flash_messages,
      is_joined = is_joined
    )



@courses_bp.route("/courses")
def courses():
   page=request.args.get('page', 1, type=int)
   courses=Course.query.paginate(page= page, per_page= 6)
   return render_template("courses.html", title="Courses", courses = courses)



@courses_bp.route("/dashboard/new_course", methods=["GET","POST"])
@login_required
def new_course():
  new_course_form=NewCourseForm()
  if new_course_form.validate_on_submit(): 
     
     if new_course_form.icon_image.data:
        icon_file=save_picture(new_course_form.icon_image.data,
                               path="static/images/course_pics")
        
     category=new_course_form.category.data

     course=Course(title=new_course_form.title.data,
                  description=new_course_form.description.data,
                  icon=icon_file,
                  author=current_user,
                  price=int(new_course_form.price.data),
                  category=category
                  )
     
     db.session.add(course)
     db.session.commit()

     flash("The course has been created",category="success")
     return redirect(url_for("courses_bp.new_course"))

  categories=Category.query.all()
  flash_messages = get_flashed_messages()

  return render_template("new_course.html",
                        title="New Course",
                        new_course_form=new_course_form,
                        active_tab="new_course",
                        categories=categories,
                        flash_messages=flash_messages
                        )


@courses_bp.route("/dashboard/your_courses", methods=["GET", "POST"])
@login_required
def your_courses(): 
   courses=Course.query.all()
   flash_messages = get_flashed_messages()

   return render_template(
      "your_courses.html", 
      title="Courses", 
      active_tab="your_courses",
      courses=courses,
      flash_messages = flash_messages
      
    )


@courses_bp.route("/delete_course/<string:course_title>", methods=["GET","POST"])
@login_required
def delete_course(course_title):
   course=Course.query.filter_by(title=course_title).first_or_404()
   
   
   if course.author != current_user:
      abort(403)
   delete_picture(course.icon, path="static/images/course_pics")
   db.session.delete(course)
   db.session.commit()
  
   flash("Your Course has been deleted!", "success")
   return redirect(url_for("courses_bp.your_courses"))


@courses_bp.route("/update_course/<string:course_title>", methods=["GET", "POST"])
@login_required
def update_course(course_title):
  course=Course.query.filter_by(title=course_title).first_or_404()


  # modify this to check if the user he want update this course is 
  # admin instead of author of the course
  if course.author != current_user:
      abort(403)

  update_course_form = UpdateCourseForm()
  if update_course_form.validate_on_submit():
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
     "update_course.html",
     course = course,
     update_course_form = update_course_form 

  )


@courses_bp.route("/edit-course/<string:course_title>", methods=["GET", "POST"])
@login_required
def edit_course(course_title): 
   course=Course.query.filter_by(title=course_title).first_or_404()
   units=Unit.query.filter_by(course=course).order_by(Unit.number).all()

   unit_lessons = {} # Dictionary to store lessons for each unit

   for unit in units:
      # Fetch lessons for the current unit
      lessons = Lesson.query.filter_by(unit=unit).all()
      unit_lessons[unit.id] = lessons  # Store lessons for the unit

   
   return render_template( "edit-course.html", 
                          title = course.title,
                          course = course,
                          units = units,
                          unit_lessons = unit_lessons
                          )
