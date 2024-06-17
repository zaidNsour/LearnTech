def getAverageReviewFromComments(comments):
 
  if comments: 
    sum=0
    for comment in comments:
      sum += comment.rating

    return sum / len(comments)
  
  else:
    return 0