from website.models import Course, Category
from flask import render_template, url_for, flash, redirect, request
from website.dashboard.forms import  UpdateProfileForm
from website import db
from flask_login import (
    login_required,
    current_user,
)
from website.helper import instructor_required, save_picture
from flask import get_flashed_messages, Blueprint

dashboard_bp=Blueprint('dashboard_bp',__name__, url_prefix='/dashboard')


# check for the default_category
@dashboard_bp.route("/",methods=["GET", "POST"])
@login_required
def dashboard():
  default_category = Category.query.first()
  flash_messages = get_flashed_messages()
  return render_template("dashboard/dashboard.html",
                          title= "dashboard",
                          default_category= default_category.title,
                          flash_messages= flash_messages,
                           active_tab= "profile")


@dashboard_bp.route("/profile", methods=["GET","POST"])
@login_required
def profile(): 
  profile_form = UpdateProfileForm()
  if profile_form.validate_on_submit():
     
    if profile_form.image.data:
      picture_file = save_picture(profile_form.image.data,
                                path="static/images/user_pics",
                                output_size=(200,200) 
                                )
      current_user.img_file = picture_file


    if profile_form.email.data is not None:  # disable email changing
        current_user.email = profile_form.email.data
      
    current_user.bio = profile_form.bio.data
    db.session.commit()
    flash("your Profile has currently Updated",category = "success")
    return redirect(url_for("dashboard_bp.profile"))
  
  elif request.method == 'GET':
    profile_form.bio.data = current_user.bio
    profile_form.email.data = current_user.email

  img_file = url_for("static", filename= f"images/user_pics/{current_user.img_file}")

  flash_messages = get_flashed_messages()

  return render_template("dashboard/profile.html", title= "Profile", profile_form= profile_form,
                          img_file= img_file, active_tab= "profile", flash_messages= flash_messages
                        )



@dashboard_bp.route("/your_courses", methods=["GET"])
@instructor_required
def your_courses(): 
   courses= Course.query.filter_by(instructor_id= current_user.id).all()
   flash_messages = get_flashed_messages()

   return render_template(
      "dashboard/your_courses.html", 
      title="Your Courses", 
      active_tab= "your_courses",
      courses= courses,
      flash_messages = flash_messages
    )

