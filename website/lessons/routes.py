from website.models import  Lesson, Course, Unit, LessonComment
from flask import render_template, url_for, flash, redirect, request
from website.lessons.forms import NewLessonForm, NewLessonCommentForm, UpdateLessonForm
from website import db

from flask_login import (
    login_required,
    current_user,
    login_required,
)
from flask import get_flashed_messages

###methods###
from website.helper import get_youtube_thumbnail_from_url
from website.lessons.helper import choice_query_unit, get_previous_next_lesson


from flask import Blueprint
lessons_bp=Blueprint("lessons_bp",__name__)



@lessons_bp.route("/<string:course_title>/<string:lesson_title>", methods=['GET', 'POST'])
@login_required
def course_content(course_title, lesson_title):
    
    course = Course.query.filter_by(title=course_title).first_or_404()

    # modify this to matched the progress of students not first lesson
    current_lesson=Lesson.query.filter_by(title=lesson_title, course=course).first()
  
    if current_lesson:
      previous_lesson, next_lesson = get_previous_next_lesson(current_lesson)
      lesson_thumbnail= get_youtube_thumbnail_from_url(current_lesson.video_url)
      comments=LessonComment.query.filter_by(lesson_id=current_lesson.id).all()
      units=Unit.query.filter_by(course=course).all()
      unit_lessons = {} # Dictionary to store lessons for each unit

      for unit in units:
        # Fetch lessons for the current unit
        lessons = Lesson.query.filter_by(unit=unit).all()
        unit_lessons[unit.id] = lessons  # Store lessons for the unit

      form = NewLessonCommentForm()
      if request.method == 'POST' and form.validate_on_submit():
        new_comment = LessonComment(
        lesson=current_lesson,
        user=current_user,
        title=form.title.data,
        details=form.details.data,
        rating=form.rating.data
        ) 
        db.session.add(new_comment)
        db.session.commit() 
        # Redirect to the same page to avoid form resubmission
        return redirect(url_for('lessons_bp.course_content', course_title=course_title, lesson_title=lesson_title))

      flash_messages = get_flashed_messages()

      return render_template(
        "course_content.html",
        title=course.title,
        course=course,
        units=units,
        current_lesson=current_lesson,
        unit_lessons=unit_lessons, 
        lesson_thumbnail=lesson_thumbnail,
        flash_messages=flash_messages,
        previous_lesson=previous_lesson,
        next_lesson= next_lesson,  
        comments=comments, 
        form=form  # Pass the form instance to the template  
        )
    else:

      return render_template("coming-soon.html")
    


@lessons_bp.route("/new_lesson/<string:course_title>", methods=["GET","POST"])
@login_required
def new_lesson(course_title):

  form = NewLessonForm()
  form.unit.query_factory = lambda: choice_query_unit(course_title)

  if form.validate_on_submit():
    course = Course.query.filter_by(title = course_title).first_or_404()

    unit = form.unit.data
     
    lessons = Lesson.query.filter_by(course = course).order_by(Lesson.number).all()
    insert_position = len(lessons) + 1

    for idx, lesson in reversed( list( enumerate(lessons) ) ) :
      if lesson.unit == unit:
        insert_position = idx + 1
        break
        
    # Shift the numbers of the following lessons
    for lesson in lessons[insert_position - 1:]:
      lesson.number += 1     


    lesson=Lesson(title = form.title.data,
                  details = form.details.data,
                  video_url = form.video_url.data,
                  course = course,
                  unit = unit,
                  number = insert_position
                  )   
    
    Lesson.renumber_lessons(course)

    db.session.add(lesson)
    db.session.commit()

    Lesson.renumber_lessons(lesson.course)

    flash("Your lesson has been created!", "success")
    return redirect( url_for("courses_bp.edit_course", course_title = course.title))
  
  flash_messages = get_flashed_messages()
  
  return render_template(
        "new_lesson.html",
        title="New Lesson",
        form = form,
        flash_messages=flash_messages,
    )
    

@lessons_bp.route("/update_lesson/<string:course_title>/<string:lesson_title>", methods=["GET", "POST"])
@login_required
def update_lesson(course_title, lesson_title):

  course=Course.query.filter_by(title=course_title).first()
  lesson = Lesson.query.filter_by(course_id = course.id, title = lesson_title).first_or_404()

  form = UpdateLessonForm()
  form.course.data = course
  if form.validate_on_submit():
    lesson.title = form.title.data
    lesson.details = form.details.data
    lesson. video_url = form.video_url.data

    db.session.commit()
    flash("The Lesson has been updated!", "success")
    return redirect( url_for("courses_bp.edit_course", course_title = course.title)) 
  
  elif request.method == 'GET':
     form.title.data = lesson.title
     form.details.data = lesson.details
     form.video_url.data = lesson.video_url
  return render_template(
     "update_lesson.html",
     course = course,
     lesson = lesson,
     form = form 

  )
    

@lessons_bp.route("/delete_lesson/<string:course_title>/<string:lesson_title>", methods=["GET","POST"])
@login_required
def delete_lesson(course_title, lesson_title):
   course = Course.query.filter_by(title = course_title).first()
   lesson=Lesson.query.filter_by(course_id = course.id,title=lesson_title).first_or_404()
   
   try:
        db.session.delete(lesson)
        db.session.commit()
        Lesson.renumber_lessons(lesson.course)
        flash("The Lesson has been deleted!", "success")

   except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the lesson.", "error")
        print(f"Error deleting lesson: {e}")
  

   return redirect( url_for("courses_bp.edit_course", course_title = course.title)) 
    