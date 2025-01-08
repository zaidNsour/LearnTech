from flask import current_app
import secrets
from PIL import Image
import os
from website.models import Course, Category
from flask import current_app, redirect, request, flash, url_for
from flask_login import current_user
from functools import wraps
from flask_login import current_user, login_required



def save_picture( form_picture, path, output_size=None ):
	random_hex=secrets.token_hex(8)
	#return the extension of an Image and ignore the name of it
	_, picture_ext = os.path.splitext(form_picture.filename) 
	picture_name= random_hex + picture_ext
	picture_path= os.path.join(current_app.root_path, path, picture_name)
	i=Image.open(form_picture)
	if output_size:
		output_size=output_size
		i.thumbnail(output_size)
	i.save(picture_path)
	return picture_name


def delete_picture(picture_name, path):
    picture_path = os.path.join(current_app.root_path, path, picture_name)
    try:
        os.remove(picture_path)
    except:
        pass
    

def lessonCountInCourse(course_id):
    count = 0
    course = Course.query.get(course_id)
    if course:
        count = sum(len(unit.lessons) for unit in course.units)
    return count



def choice_query_category():
  return Category.query 

def choice_query_course():
  return Course.query.filter_by(author = current_user) 


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        user = current_user
        if not user or not user.is_admin:
            flash("Admin access required.", category="error")
            return redirect(request.referrer or url_for("main.home")) 
        return fn(*args, **kwargs)
    return wrapper


def instructor_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        user = current_user
        if not user or not user.is_instructor:
            flash("Instructor access required.", category="error")
            return redirect(request.referrer or url_for("main.home")) 
        return fn(*args, **kwargs)
    return wrapper

