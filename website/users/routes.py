from website.models import User, Course, Category, JoinedCourse
from flask import render_template, url_for, flash, redirect, request
from website.users.forms import RegistrationForm, LoginForm, UpdateProfileForm
from website.users.forms import RequestResetPasswordForm, ResetPasswordForm
from website import bcrypt, db
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user,
    login_required,
)
from flask import get_flashed_messages

###methods###
from website.helper import lessonCountInCourse, save_picture
from website.users.helper import send_reset_email


from flask import Blueprint
users_bp=Blueprint('users_bp',__name__)


@users_bp.route("/register", methods=["POST","GET"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for("main.home"))
  #decode("utf-8") to convert password into string
  form=RegistrationForm()

  if form.validate_on_submit():
    hashed_password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
    user=User(fname=form.fname.data, lname=form.lname.data, email=form.email.data,
              password=hashed_password, is_instructor=False, is_admin=False)
    db.session.add(user)
    db.session.commit()
    flash(message="Account created successfully",category="success")
    return redirect( url_for("users_bp.login") )
  
  flash_messages = get_flashed_messages()
  return render_template("register.html",
                         title="Register", 
                         form=form,
                         flash_messages= flash_messages
                         )


@users_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
       
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))

        else:
            flash("Invalid email or password", "error")
            # Pass the form back to the template with errors
            flash_messages = get_flashed_messages() 
            return render_template("login.html", title="Login", form=form,flash_messages= flash_messages)
             
    
    flash_messages = get_flashed_messages() 
    return render_template("login.html", title="Login",
                           form= form, flash_messages= flash_messages)


@users_bp.route("/logout")
def logout():
  logout_user()
  return redirect(url_for("main.home"))



@users_bp.route("/dashboard",methods=["GET", "POST"]) #GET for review POST for update
@login_required
def dashboard():
  default_category=Category.query.first()
  flash_messages = get_flashed_messages()
  return render_template("dashboard.html",
                          title="dashboard",
                          default_category=default_category.title,
                          flash_messages=flash_messages,
                           active_tab="profile")



@users_bp.route("/dashboard/profile", methods=["GET","POST"])
@login_required
def profile(): 
  profile_form=UpdateProfileForm()
  if profile_form.validate_on_submit():
     
     if profile_form.picture.data:
        picture_file=save_picture(profile_form.picture.data,
                                  path="static/images/user_pics",
                                  output_size=(200,200) 
                                )
        current_user.img_file=picture_file


     if profile_form.email.data is not None:  # Check if email data is not None
        current_user.email = profile_form.email.data
      
     current_user.bio=profile_form.bio.data
     db.session.commit()
     flash("your Profile has currently Updated",category="success")
     return redirect(url_for("users_bp.profile"))
  
  elif request.method == 'GET':
    profile_form.bio.data=current_user.bio
    profile_form.email.data=current_user.email

  img_file = url_for("static", filename=f"images/user_pics/{current_user.img_file}")

  flash_messages = get_flashed_messages()

  return render_template("profile.html",
                          title="Profile",
                          profile_form=profile_form,
                          img_file=img_file, active_tab="profile",
                          flash_messages=flash_messages
                        )


@users_bp.route("/enroll_user/<string:course_title>", methods=['GET', 'POST'])
@login_required
def enroll_user(course_title):
  
  course = Course.query.filter_by(title=course_title).first_or_404()
  new_enrollment = JoinedCourse(user_id=current_user.id,course_id=course.id)
  db.session.add(new_enrollment)
  db.session.commit()

  flash_messages = get_flashed_messages()
  
  return render_template(
    "enroll_done.html",
    title="Enroll done",
    flash_messages=flash_messages
    )


@users_bp.route("/my_learning", methods=['GET'])
@login_required
def my_learning():
  my_courses = db.session.query(Course).join(JoinedCourse).filter(JoinedCourse.user_id == current_user.id).all()
  flash_messages = get_flashed_messages()
  return render_template(
        "my_learning.html",
        title="My Learning",
          my_courses = my_courses,
        flash_messages=flash_messages
    )


@users_bp.route("/author_info/<int:author_id>", methods=['GET'])
def author_info(author_id):
  author=User.query.filter_by(id=author_id).first_or_404()
  courses=Course.query.filter_by(author= author).all() #lessonCountInCourse()
  lessons_count={}
  for course in courses:
     lessons_count[course.id]= lessonCountInCourse(course.id)
  return render_template("author.html",
                          courses= courses,
                          author= author,
                          lessons_count= lessons_count
                        ) 


@users_bp.route("/reset_password", methods=['GET','POST'])
def reset_request():
   if current_user.is_authenticated:
      return redirect(url_for('main.home'))
   form = RequestResetPasswordForm()
   if form.validate_on_submit():
      user=User.query.filter_by(email= form.email.data).first()
      if user:
         send_reset_email(user)
         flash('If this account exist, you will recieve an email with isntruction', 'info')
         return redirect(url_for('users_bp.login'))
   return render_template('reset_request.html', title= 'Reset Password' ,form= form)


@users_bp.route("/reset_password/<token>", methods=['GET','POST'])
def reset_password(token):
   if current_user.is_authenticated:
      return redirect(url_for('main.home'))
   
   user= User.verify_reset_token(token)
   if not user:
      flash('The token is invalid or expired', 'warning')
      return redirect(url_for('users_bp.reset_request'))
   
   form= ResetPasswordForm()
   if form.validate_on_submit():
      hashed_password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
      user.password= hashed_password
      db.session.commit()
    
      flash(message="your Password has been updated successfully",category="success")
      return redirect( url_for("users_bp.login") )    
      
   return render_template('reset_password.html', title='Reset Password', form = form)