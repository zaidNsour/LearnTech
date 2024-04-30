import secrets
from flask_mail import Message
from PIL import Image
import os
from os import abort
from website.models import User, Lesson, Course, Category, Unit, LessonComment, JoinedCourse
from flask import render_template, url_for, flash, redirect, request,Blueprint
from flask import jsonify
from website.forms import RegistrationForm, LoginForm, UpdateProfileForm, UpdateCourseForm
from website.forms import NewLessonForm, NewCourseForm, NewUnitForm
from website.forms import NewCategoryForm,NewLessonCommentForm
from website.forms import RequestResetPasswordForm, ResetPasswordForm
from website import app, bcrypt, db, mail
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user,
    login_required,
)
from flask import get_flashed_messages
from sqlalchemy import func
from sqlalchemy.orm.exc import StaleDataError

from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs




routes=Blueprint("routes",__name__)


#----------------------methods----------------------------
def save_picture( form_picture, path, output_size=None ):
	random_hex=secrets.token_hex(8)
	#return the extension of an Image and ignore the name of it
	_, picture_ext = os.path.splitext(form_picture.filename) 
	picture_name= random_hex + picture_ext
	picture_path= os.path.join(app.root_path, path, picture_name)
	i=Image.open(form_picture)
	if output_size:
		output_size=output_size
		i.thumbnail(output_size)
	i.save(picture_path)
	return picture_name


def delete_picture(picture_name, path):
    picture_path = os.path.join(app.root_path, path, picture_name)
    try:
        os.remove(picture_path)
    except:
        pass


def CourseCountInCategory(category_id):
   courses=Course.query.filter_by(category_id=category_id).all()
   return len(courses)

def lessonCountInCourse(course_id):
    count = 0
    course = Course.query.get(course_id)
    if course:
        count = sum(len(unit.lessons) for unit in course.units)
    return count

def getMaxNumberInLesson(course_id):
  return db.session.query(func.max(Lesson.number)).filter_by(course_id=course_id).scalar() or 0 

def getMaxNumberInUnit(course_id):
  return db.session.query(func.max(Unit.number)).filter_by(course_id=course_id).scalar() or 0 


API_KEY = 'AIzaSyBHA-rIMchSMmjrnNRZoODQf9GD5KGTyDQ'

# Initialize the YouTube Data API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to fetch the thumbnail URL of a YouTube video
def get_youtube_thumbnail(video_id):
    response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()
    items = response.get('items', [])
    if items:
        return items[0]['snippet']['thumbnails']['default']['url']
    else:
        return None
    
def get_high_resolution_thumbnail(video_id):
    response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()
    items = response.get('items', [])
    if items:
        return items[0]['snippet']['thumbnails'].get('maxres', {}).get('url')
    else:
        return None


def get_video_id_from_url(video_url):
    parsed_url = urlparse(video_url)
    if parsed_url.hostname == 'www.youtube.com' or parsed_url.hostname == 'youtube.com':
        if 'v' in parse_qs(parsed_url.query):
            return parse_qs(parsed_url.query)['v'][0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    return None

# Function to fetch the thumbnail URL of a YouTube video
def get_youtube_thumbnail_from_url(video_url):
    video_id = get_video_id_from_url(video_url)
    if video_id:
        return get_high_resolution_thumbnail(video_id)
    else:
        return None
   

def get_previous_next_lesson(lesson):
  if lesson:
    
    course = lesson.course 
    number=lesson.number

    lesson_count = Lesson.query.filter_by(course=course).count()

    # Calculate the previous and next lesson numbers
    previous_number = number - 1 if number > 1 else None
    next_number = number + 1 if number < lesson_count else None

    # Query the previous and next lessons based on the calculated numbers
    previous_lesson = Lesson.query.filter_by(course_id=course.id, number=previous_number).first() if previous_number else None
    next_lesson = Lesson.query.filter_by(course_id=course.id, number=next_number).first() if next_number else None
                       
    return previous_lesson, next_lesson
  else:
     return None , None
  
  
#use _external because redirect from email to this route 
def send_reset_email(user):
   token= user.get_reset_token()
   #change email
   msg=Message('Password reset request', sender= 'aaa@gmail.com',
               recipients= [user.email],
               body=f''' To reset your password, visit the following link:
               {url_for('reset_password', token=token, _external=True)}  
                if you did not make this request, please ignore this email'''
              )
   mail.send(msg)
   
   

#----------------------methods----------------------------


@app.route("/", methods=["GET", "POST"] )
def home():
  courses=Course.query.limit(6).all()
  categories=Category.query.all()
  flash_messages = get_flashed_messages()
  return render_template("home.html",  
                         courses= courses,
                         categories= categories,
                         flash_messages= flash_messages
                         )



@app.route("/register", methods=["POST","GET"])
def register():
  if current_user.is_authenticated:
    return redirect(url_for(home))
  #decode("utf-8") to convert password into string
  form=RegistrationForm()

  if form.validate_on_submit():
    hashed_password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
    user=User(fname=form.fname.data, lname=form.lname.data, email=form.email.data,
              password=hashed_password, is_instructor=False, is_admin=False)
    db.session.add(user)
    db.session.commit()
    flash(message="Account created successfully",category="success")
    return redirect( url_for("login") )
  
  flash_messages = get_flashed_messages()
  return render_template("register.html",
                         title="Register", 
                         form=form,
                         flash_messages= flash_messages
                         )


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
       
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))

        else:
            flash("Invalid email or password", "error")
            # Pass the form back to the template with errors
            flash_messages = get_flashed_messages() 
            return render_template("login.html", title="Login", form=form,flash_messages= flash_messages)
             
    
    flash_messages = get_flashed_messages() 
    return render_template("login.html", title="Login",
                           form= form, flash_messages= flash_messages)


@app.route("/logout")
def logout():
  logout_user()
  return redirect(url_for("home"))



@app.route("/about")
def about():
  return render_template("about.html", title="About Us")



@app.route("/contact")
def contact():
  return render_template("contact.html", title="Contact With Us")



@app.route("/faq")
def faq():
  return render_template("faq.html", title="FAQ")



@app.route("/courses")
def courses():
   page=request.args.get('page', 1, type=int)
   courses=Course.query.paginate(page= page,per_page= 6)
   return render_template("courses.html", title="Courses", courses = courses)




@app.route("/dashboard",methods=["GET", "POST"]) #GET for review POST for update
@login_required
def dashboard():
  default_category=Category.query.first()
  flash_messages = get_flashed_messages()
  return render_template("dashboard.html",
                          title="dashboard",
                          default_category=default_category.title,
                          flash_messages=flash_messages,
                           active_tab="profile")



@app.route("/dashboard/profile", methods=["GET","POST"])
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
     return redirect(url_for("profile"))
  
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





@app.route("/get_units", methods=["GET"])
@login_required
def get_units():
  """
  This route retrieves units based on the provided course ID in the query parameter.
  """
  course_id = request.args.get("course_id")  # Get the course ID from the query parameter
  if not course_id:
    return jsonify({"error": "Missing course ID"}), 400  # Handle missing course ID

  # Filter units based on the course ID
  units = Unit.query.filter_by(course_id=course_id).all()

  # Convert units to a list of dictionaries (suitable for JSON response)
  unit_data = []
  for unit in units:
    unit_data.append({
      "id": unit.id,  # Assuming unit has an ID property
      "title": unit.title,  # Assuming unit has a title property
    })

  return jsonify(unit_data)




def choice_query_test(form):
  """
  This function dynamically filters units based on the selected course.
  """
  course = form.course.data  # Assuming 'course' field holds the ID
  
  if course:
    return Unit.query.filter_by(course_id=course.id).all()
  else:
    return []  # Return an empty list if no course is selected



@app.route("/dashboard/new_lesson", methods=["GET","POST"])
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
     return redirect(url_for("new_lesson"))
  
  flash_messages = get_flashed_messages()
  
  return render_template(
        "new_lesson.html",
        title="New Lesson",
        new_lesson_form=new_lesson_form,
        active_tab="new_lesson",
        flash_messages=flash_messages
    )




@app.route("/dashboard/new_unit", methods=["GET","POST"])
@login_required
def new_unit():
  new_unit_form=NewUnitForm()
  course=new_unit_form.course.data
  if new_unit_form.validate_on_submit():
     unit=Unit(title= new_unit_form.title.data,
               course=course,
               number=getMaxNumberInUnit(course.id) + 1
                  )
     db.session.add(unit)
     db.session.commit()

     flash("Unit has been created!", "success")
     return redirect(url_for("new_unit"))
  
  flash_messages = get_flashed_messages()
  
  return render_template(
        "new_unit.html",
        title="New Unit",
        new_unit_form=new_unit_form,
        active_tab="new_unit",
        flash_messages=flash_messages
    )




@app.route("/dashboard/new_course", methods=["GET","POST"])
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
     return redirect(url_for("new_course"))

  categories=Category.query.all()
  flash_messages = get_flashed_messages()

  return render_template("new_course.html",
                        title="New Course",
                        new_course_form=new_course_form,
                        active_tab="new_course",
                        categories=categories,
                        flash_messages=flash_messages
                        )




@app.route("/dashboard/new_category", methods=["GET","POST"])
@login_required
def new_category():
  new_category_form=NewCategoryForm()

  if new_category_form.validate_on_submit():
     if new_category_form.icon_image.data:
        icon_file=save_picture(new_category_form.icon_image.data,
                               path="static/images/category_pics")
     category=Category(title= new_category_form.title.data,
                      icon=icon_file
                       )
     db.session.add(category)
     db.session.commit()

     flash("Category has been created!", "success")
     return redirect(url_for("new_category"))
  
  flash_messages = get_flashed_messages()
  
  return render_template(
        "new_category.html",
        title="New Category",
        new_category_form=new_category_form,
        active_tab="new_category",
        flash_messages=flash_messages
    )


@app.route("/dashboard/your_courses", methods=["GET", "POST"])
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



@app.route("/delete_course/<string:course_title>", methods=["GET","POST"])
@login_required
def delete_course(course_title):
   course=Course.query.filter_by(title=course_title).first_or_404()
   delete_picture(course.icon, path="static/images/course_pics")
   
   if course.author != current_user:
      abort(403)

   db.session.delete(course)
   db.session.commit()
  
   flash("Your Course has been deleted!", "success")
   return redirect(url_for("your_courses"))


@app.route("/update_course/<string:course_title>", methods=["GET", "POST"])
@login_required
def update_course(course_title):
  course=Course.query.filter_by(title=course_title).first_or_404()

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
    return redirect(url_for("your_courses"))
  
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



@app.route("/category/<string:category_title>")
def category_list(category_title):
    
    category = Category.query.filter_by(title=category_title).first_or_404()
    category_courses=Course.query.filter_by(category_id=category.id)
    categories=Category.query.all()
    courses_count=CourseCountInCategory(category.id)
    return render_template(
        "category.html",
        title=category.title,
        category=category,
        category_courses=category_courses,
        categories=categories,
        courses_count=courses_count
      )



@app.route("/<string:course_title>",  methods=['GET', 'POST'])
def course(course_title):
    course = Course.query.filter_by(title=course_title).first_or_404() 
    related_courses=Course.query.filter_by(category=course.category).all()
    #lesson thats user arrive to it 
    current_lesson=Lesson.query.filter_by(course_id= course.id).first()
   
    return render_template(
        "course.html",
        title=course.title,
        course=course,
        related_courses=related_courses,
        current_lesson=current_lesson
    )


@app.route("/<string:course_title>/<string:lesson_title>", methods=['GET', 'POST'])
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
      return redirect(url_for('course_content', course_title=course_title, lesson_title=lesson_title))


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
    



  


@app.route("/<string:course_title>/enroll_user", methods=['POST'])
@login_required
def enroll_user(course_title):
  if request.method == 'POST':
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


@app.route("/my_learning", methods=['GET'])
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


@app.route("/author_info/<int:author_id>", methods=['GET'])
def author_info(author_id):
  #page=request.args.get('page', 1, type=int)
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


@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
   if current_user.is_authenticated:
      return redirect(url_for('home'))
   form = RequestResetPasswordForm()
   if form.validate_on_submit():
      user=User.query.filter_by(email= form.email.data).first()
      if user:
         send_reset_email(user)
         flash('If this account exist, you will recieve an email with isntruction', 'info')
         return redirect(url_for('login'))
   return render_template('reset_request.html', title= 'Reset Password' ,form= form)


@app.route("/reset_password/<string:token>", methods=['GET','POST'])
def reset_password(token):
   if current_user.is_authanticated:
      return redirect(url_for('home'))
   
   user= User.verify_reset_token(token)
   if not user:
      flash('The token is invalid or expired', 'warning')
      return redirect(url_for('reset_request'))
   
   form= ResetPasswordForm()
   if form.validate_on_submit():
    hashed_password=bcrypt.generate_password_hash(form.password.data).decode("utf-8")
    user.password= hashed_password
    db.session.commit()
    
    flash(message="your Password has been updated successfully",category="success")
    return redirect( url_for("login") )    
      
   return render_template('reset_password.html', title='Reset Password', form= form)



   




































    







