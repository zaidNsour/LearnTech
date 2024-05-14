from website.models import Course, Category
from flask import render_template, request
from flask import get_flashed_messages
from website.main.forms import SearchForm

### Methods ###
from website.main.helper import rank_courses


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



@main.route("/contact")
def contact():
  return render_template("contact.html", title="Contact With Us")



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
  
  

  





