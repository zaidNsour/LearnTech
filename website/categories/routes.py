from website.models import  Course, Category
from flask import render_template
from website.categories.helper import CourseCountInCategory

from flask import Blueprint
categories_bp=Blueprint("categories_bp", __name__, url_prefix= "/categories")


@categories_bp.route("/<string:category_title>")
def category_list(category_title):
    
    category = Category.query.filter_by(title= category_title).first_or_404()
    category_courses=Course.query.filter_by(category_id= category.id)
    categories= Category.query.all()
    return render_template(
        "categories/category.html",
        title= category.title,
        category= category,
        category_courses= category_courses,
        categories= categories,
        courses_count= CourseCountInCategory(category.id)
      )
