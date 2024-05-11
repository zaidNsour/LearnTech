from website.models import  Lesson, Course, Unit, LessonComment
from flask import render_template, url_for, flash, redirect, request
from website.lessons.forms import NewLessonForm, NewLessonCommentForm
from website import db

from flask_login import (
    login_required,
    current_user,
    login_required,
)
from flask import get_flashed_messages

###methods###
from website.helper import get_youtube_thumbnail_from_url
from website.lessons.helper import choice_query_test, getMaxNumberInLesson, get_previous_next_lesson



from flask import Blueprint
lessons_bp=Blueprint("lessons_bp",__name__)


@lessons_bp.route("/dashboard/new_lesson", methods=["GET","POST"])
@login_required
def new_lesson():

  new_lesson_form=NewLessonForm()
  new_lesson_form.unit.query_factory = lambda: choice_query_test(new_lesson_form)


  if new_lesson_form.validate_on_submit():
     course=new_lesson_form.course.data

     unit=new_lesson_form.unit.data

     lesson=Lesson(title=new_lesson_form.title.data,
                  details=new_lesson_form.details.data,
                  video_url=new_lesson_form.video_url.data,
                  course=course,
                  unit=unit,
                  number=getMaxNumberInLesson(course.id) + 1
                  )
     
     db.session.add(lesson)
     db.session.commit()

     flash("Your lesson has been created!", "success")
     return redirect(url_for("lessons_bp.new_lesson"))
  
  flash_messages = get_flashed_messages()
  
  return render_template(
        "new_lesson.html",
        title="New Lesson",
        new_lesson_form=new_lesson_form,
        active_tab="new_lesson",
        flash_messages=flash_messages
    )

@lessons_bp.route("/<string:course_title>/<string:lesson_title>", methods=['GET', 'POST'])
@login_required
def course_content(course_title, lesson_title):
    
    course = Course.query.filter_by(title=course_title).first_or_404()
    units=Unit.query.filter_by(course=course).all()
    current_lesson=Lesson.query.filter_by(title=lesson_title, course=course).first()
    there_lesson=False
    lesson_thumbnail = None
    unit_lessons = {} # Dictionary to store lessons for each unit
    previous_lesson, next_lesson=None, None
    comments = []
   

    if current_lesson:
      previous_lesson, next_lesson = get_previous_next_lesson(current_lesson)
      lesson_thumbnail= get_youtube_thumbnail_from_url(current_lesson.video_url)
      comments=LessonComment.query.filter_by(lesson_id=current_lesson.id).all()
      there_lesson=True   
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
        there_lesson=there_lesson,
        flash_messages=flash_messages,
        previous_lesson=previous_lesson,
        next_lesson= next_lesson,  
        comments=comments, 
        form=form  # Pass the form instance to the template  
    )
    