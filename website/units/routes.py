from website.models import  Unit
from flask import render_template, url_for, flash, redirect, request,Blueprint
from flask import jsonify
from website.units.forms import NewUnitForm
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


@units_bp.route("/dashboard/new_unit", methods=["GET","POST"])
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
     return redirect(url_for("units_bp.new_unit"))
  
  flash_messages = get_flashed_messages()
  
  return render_template(
        "new_unit.html",
        title="New Unit",
        new_unit_form=new_unit_form,
        active_tab="new_unit",
        flash_messages=flash_messages
    )
