from website.models import  Course, Lesson, Unit
from flask import render_template, url_for, flash, redirect, request,Blueprint
from flask import jsonify
from website.units.forms import NewUnitForm, UpdateUnitForm
from website import  db
from flask_login import login_required
from flask import get_flashed_messages

###methods###
from website.units.helper import getMaxNumberInUnit


from flask import Blueprint
units_bp=Blueprint("units_bp",__name__)


@units_bp.route("/get_units", methods=["GET"])
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


@units_bp.route("/new_unit/<string:course_title>", methods=["GET","POST"])
@login_required
def new_unit(course_title):

  course = Course.query.filter_by(title = course_title).first_or_404()
  form=NewUnitForm()
  form.course.data = course

  if form.validate_on_submit(): 
     unit=Unit(title= form.title.data,
               course = course,
               number=getMaxNumberInUnit(course.id) + 1
                  )
     db.session.add(unit)
     db.session.commit()

     flash("Unit has been created!", "success")
     return redirect( url_for("courses_bp.edit_course", course_title = course.title)) 
  
  return render_template(
        "new_unit.html",
        title = "New Unit",
        form = form,
        flash_messages = get_flashed_messages()
    )


@units_bp.route("/update_unit/<string:course_title>/<string:unit_title>", methods=["GET", "POST"])
@login_required
def update_unit(course_title, unit_title):

  course=Course.query.filter_by(title=course_title).first()
  unit = Unit.query.filter_by(course = course, title = unit_title).first_or_404()
  form = UpdateUnitForm()
  form.course.data = course

  if form.validate_on_submit():
    unit.title = form.title.data
    db.session.commit()
    flash("The Unit has been updated!", "success")
    return redirect( url_for("courses_bp.edit_course", course_title = course.title)) 
  
  elif request.method == 'GET':
     form.title.data = unit.title
   
  return render_template(
     "update_unit.html",
     title = "Update Unit",
     course = course,
     unit = unit,
     form = form 

  )



@units_bp.route("/delete_unit/<string:course_title>/<string:unit_title>", methods=["GET","POST"])
@login_required
def delete_unit(course_title, unit_title):
   course = Course.query.filter_by(title = course_title).first()
   unit=Unit.query.filter_by(course = course, title=unit_title).first_or_404()
   
   try:
        db.session.delete(unit)
        db.session.commit()
        Lesson.renumber_lessons(course)
        Unit.renumber_units(course)
        flash("The Unit has been deleted!", "success")

   except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the Unit.", "error")
        print(f"Error deleting Unit: {e}")
  
   return redirect( url_for("courses_bp.edit_course", course_title = course.title)) 




@units_bp.route('/reorder_units', methods=['POST'])
def reorder_units():
    data = request.get_json()
    unit_order = data['order']
    course_id = data['course_id']
    course = Course.query.filter_by(id = course_id).first()
    
   
    # Recalculate the number of units and update their order in the database
    for index, unit_id in enumerate(unit_order):
        unit = Unit.query.get(unit_id)
        if unit:
            unit.number = index + 1
            db.session.commit()
            
    Lesson.renumber_lessons(course)
    return jsonify({'status': 'success'})


    
