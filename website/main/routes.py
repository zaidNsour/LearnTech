from website.models import Course, Category
from flask import render_template
from flask import get_flashed_messages


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
