import sys
from website.models import Course, Category
from flask import flash, redirect, render_template, request, url_for
from flask import get_flashed_messages
from website.main.forms import SearchForm, contactForm

### Methods ###
from website.main.helper import send_contact_us_email


from flask import Blueprint
main= Blueprint("main", __name__)



@main.route("/", methods=["GET", "POST"] )
def home():
  courses=Course.query.limit(6).all()
  categories=Category.query.all()
  flash_messages = get_flashed_messages()
  return render_template("home.html",  
                         courses= courses,
                         categories= categories,
                         flash_messages= flash_messages
                         )



@main.route("/about")
def about():
  return render_template("about.html", title="About Us")



@main.route("/contact", methods=["GET","POST"])
def contact():
  form= contactForm()
  if form.validate_on_submit():
    name= form.name.data
    email= form.email.data
    message= form.message.data
    
    print(f'\n\n\n Form data: {name}, {email}, {message}', file=sys.stderr) ###
    try:
      send_contact_us_email(name, email, message)
      flash('The request was successfully submitted!', 'success')
    except Exception as e:
      flash(f'An error occurred: {str(e)}', 'danger')
      print(f"\n\n\nError sending email: {e}", file=sys.stderr) ###


    return redirect(url_for('main.contact'))
  
  flash_messages = get_flashed_messages()

  print(f"\n\n\nForm not submitted or validation failed", file=sys.stderr) ###

  return render_template("contact.html", title="Contact With Us", form= form,
                         flash_messages= flash_messages)


@main.route("/faq")
def faq():
  return render_template("faq.html", title="FAQ")






#pass stuff to navbar
@main.context_processor
def app():
  form =SearchForm()
  return dict(form = form)



@main.route("/search", methods=['POST', 'GET'])
def search():
  form =SearchForm()
  page=request.args.get('page', 1, type=int)
  if form.validate_on_submit():
    query= form.query.data
    courses=Course.query.filter(Course.title.like('%'+ query +'%') )
    #courses= courses.order_by( Course.title ).all()
    paginated_courses = courses.paginate(page= page,per_page= 8)

    return render_template("search.html",
                            title="Search Results",
                            form=form, query=query,
                            paginated_courses= paginated_courses
                            )
  
  # If the form is not submitted or fails validation, render the search template with the form
  return render_template("search.html", title="Search", form=form)
  
  

  





