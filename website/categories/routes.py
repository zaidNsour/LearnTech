
from website.models import  Course, Category
from flask import render_template, url_for, flash, redirect
from website.categories.forms import NewCategoryForm
from website import db
from flask_login import login_required
from flask import get_flashed_messages

### methods ###
from website.helper import save_picture
from website.categories.helper import CourseCountInCategory


from flask import Blueprint
categories_bp=Blueprint("categories_bp", __name__)


@categories_bp.route("/dashboard/new_category", methods=["GET","POST"])
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
     return redirect(url_for("categories_bp.new_category"))
  
  flash_messages = get_flashed_messages()
  
  return render_template(
        "new_category.html",
        title="New Category",
        new_category_form=new_category_form,
        active_tab="new_category",
        flash_messages=flash_messages
    )

@categories_bp.route("/category/<string:category_title>")
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
