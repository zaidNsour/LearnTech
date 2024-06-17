from website.models import User



def choice_query_instructor():
  return User.query.filter_by(is_instructor=True)