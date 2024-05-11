from website.models import   Unit
from website import db
from sqlalchemy import func


def getMaxNumberInUnit(course_id):
  return db.session.query(func.max(Unit.number)).filter_by(course_id=course_id).scalar() or 0 

