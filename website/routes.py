import secrets
from PIL import Image
import os
from website.models import User, Lesson, Course
from flask import render_template, url_for, flash, redirect, request,Blueprint
from website.forms import RegistrationForm, LoginForm, UpdateProfileForm
from website.forms import NewLessonForm, NewCourseForm
from website import app, bcrypt, db
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user,
    login_required,
)
from flask import get_flashed_messages


routes=Blueprint("routes",__name__)


#----------------------methods----------------------------
def save_picture(form_picture):
   random_hex=secrets.token_hex(8)
   #return the extension of an Image and ignore the name of it
   _, picture_ext = os.path.splitext(form_picture.filename) 
   picture_name= random_hex + picture_ext
   picture_path= os.path.join(app.root_path, 'static/images/user_pics', picture_name)
   output_size=(300,300)
   i=Image.open(form_picture)
   i.thumbnail(output_size)
   i.save(picture_path)
   return picture_name
   

   

@routes.route("/", methods=["GET", "POST"] )
def home():
  return render_template("home.html")



@routes.route("/register", methods=["POST","GET"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for(routes.home))
  #decode("utf-8") to convert password into string
  form=RegistrationForm()
  if form.validate_on_submit():
    hashed_password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
    user=User(fname=form.fname.data, lname=form.lname.data, email=form.email.data,
              password=hashed_password, is_instructor=False)
    db.session.add(user)
    db.session.commit()
    flash(message="Account created successfully",category="success")
    return redirect(url_for("routes.login"))
  return render_template("register.html", title="Register", form=form)


@routes.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('routes.home'))

        else:
            flash("Invalid email or password", "error")
            # Pass the form back to the template with errors
            return render_template("login.html", title="Login", form=form)
             
    flash_messages = get_flashed_messages()    

    return render_template("login.html", title="Login",
                           form= form, flash_messages= flash_messages)


@routes.route("/logout")
def logout():
  logout_user()
  return redirect(url_for("routes.home"))



@routes.route("/about")
def about():
  return render_template("about.html", title="About Us")



@routes.route("/contact")
def contact():
  return render_template("contact.html", title="Contact With Us")



@routes.route("/faq")
def faq():
  return render_template("faq.html", title="FAQ")


@routes.route("/dashboard", methods=['GET']) #GET for review POST for update
@login_required
def dashboard():
  flash_messages = get_flashed_messages()

  return render_template("dashboard.html", title="dashboard",
                         flash_messages=flash_messages, active_tab="profile")


@routes.route("/dashboard/profile", methods=["GET","POST"])
@login_required
def profile(): 
  profile_form=UpdateProfileForm()
  if profile_form.validate_on_submit():
     
     if profile_form.picture.data:
        picture_file=save_picture(profile_form.picture.data)
        current_user.img_file=picture_file


     if profile_form.email.data is not None:  # Check if email data is not None
        current_user.email = profile_form.email.data
      
     current_user.bio=profile_form.bio.data
     db.session.commit()
     flash("your Profile has currently Updated",category="success")
     return redirect(url_for("routes.profile"))
  
  elif request.method == 'GET':
    profile_form.bio.data=current_user.bio
    profile_form.email.data=current_user.email

  img_file = url_for("static", filename=f"images/user_pics/{current_user.img_file}")

  return render_template("profile.html", title="Profile", profile_form=profile_form
                        ,img_file=img_file, active_tab="profile")
   



@routes.route("/dashboard/new_lesson", methods=["GET","POST"])
@login_required
def new_lesson():
   new_lesson_form=NewLessonForm()
   return render_template("new_lesson.html", title="New Lesson",
                          new_lesson_form=new_lesson_form,  active_tab="new_lesson")



@routes.route("/dashboard/new_course", methods=["GET","POST"])
@login_required
def new_course():
   new_course_form=NewCourseForm()
   return render_template("new_course.html", title="New Course",
                          new_course_form= new_course_form,  active_tab="new_course")



