def rank_courses(courses, query):
    # Implement TF-IDF ranking here
    # This is a simplified example, you may need to use a library like scikit-learn for TF-IDF calculations
    # For simplicity, this example just sorts courses alphabetically
    ranked_courses = sorted(courses, key=lambda course: course.title)  # Replace with TF-IDF ranking logic
    return ranked_courses