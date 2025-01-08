from website.models import JoinedCourse, User, Course
from flask import render_template, url_for, flash, redirect
from website.users.forms import RegistrationForm, LoginForm
from website.users.forms import RequestResetPasswordForm, ResetPasswordForm
from website import bcrypt, db
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user,
)
from flask import get_flashed_messages
from website.helper import lessonCountInCourse
from website.users.helper import send_reset_email


from flask import Blueprint
users_bp=Blueprint('users_bp',__name__, url_prefix='/users')


@users_bp.route("/register", methods=["POST","GET"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for("main.home"))
 
  form = RegistrationForm()

  if form.validate_on_submit():
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
    user = User(username= form.username.data, email= form.email.data,  password= hashed_password )
    db.session.add(user)
    db.session.commit()
    flash(message="Account created successfully",category="success")
    return redirect( url_for("users_bp.login") )
  
  flash_messages = get_flashed_messages()
  return render_template("users/register.html",
                         title= "Register", 
                         form= form,
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
             
  flash("Invalid email or password", "error")  
  flash_messages = get_flashed_messages() 
  return render_template("users/login.html", title="Login",
                           form= form, flash_messages= flash_messages)


@users_bp.route("/logout")
def logout():
  logout_user()
  return redirect(url_for("main.home"))


@users_bp.route("/author_info/<int:author_id>", methods=['GET'])
def author_info(author_id):
  author= User.query.filter_by(id= author_id, is_instructor = True).first_or_404()
  courses= Course.query.filter_by(author= author).all()
  lessons_count={}
  for course in courses:
     lessons_count[course.id]= lessonCountInCourse(course.id)
  return render_template("users/author.html",
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
   return render_template('users/reset_request.html', title= 'Reset Password' ,form= form)


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
      hashed_password= bcrypt.generate_password_hash(form.password.data).decode("utf-8")
      user.password= hashed_password
      db.session.commit()
    
      flash(message="your Password has been updated successfully",category="success")
      return redirect( url_for("users_bp.login") )    
      
   return render_template('users/reset_password.html', title='Reset Password', form = form)




@users_bp.route("/my_learning", methods=['GET'])
@login_required
def my_learning():
  my_courses = db.session.query(Course).join(JoinedCourse).filter(JoinedCourse.user_id == current_user.id).all()
  flash_messages = get_flashed_messages()
  return render_template(
        "users/my_learning.html",
        title="My Learning",
          my_courses = my_courses,
        flash_messages=flash_messages
    )   



