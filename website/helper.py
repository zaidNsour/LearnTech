from flask import current_app
import secrets
from PIL import Image
import os
from website.models import Course, Category
from flask import current_app
from flask_login import current_user
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs




def save_picture( form_picture, path, output_size=None ):
	random_hex=secrets.token_hex(8)
	#return the extension of an Image and ignore the name of it
	_, picture_ext = os.path.splitext(form_picture.filename) 
	picture_name= random_hex + picture_ext
	picture_path= os.path.join(current_app.root_path, path, picture_name)
	i=Image.open(form_picture)
	if output_size:
		output_size=output_size
		i.thumbnail(output_size)
	i.save(picture_path)
	return picture_name


def delete_picture(picture_name, path):
    picture_path = os.path.join(current_app.root_path, path, picture_name)
    try:
        os.remove(picture_path)
    except:
        pass
    

def lessonCountInCourse(course_id):
    count = 0
    course = Course.query.get(course_id)
    if course:
        count = sum(len(unit.lessons) for unit in course.units)
    return count

API_KEY = os.environ.get('API_KEY')

# Initialize the YouTube Data API client
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to fetch the thumbnail URL of a YouTube video
def get_youtube_thumbnail(video_id):
    response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()
    items = response.get('items', [])
    if items:
        return items[0]['snippet']['thumbnails']['default']['url']
    else:
        return None
    
def get_high_resolution_thumbnail(video_id):
    response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()
    items = response.get('items', [])
    if items:
        return items[0]['snippet']['thumbnails'].get('maxres', {}).get('url')
    else:
        return None


def get_video_id_from_url(video_url):
    parsed_url = urlparse(video_url)
    if parsed_url.hostname == 'www.youtube.com' or parsed_url.hostname == 'youtube.com':
        if 'v' in parse_qs(parsed_url.query):
            return parse_qs(parsed_url.query)['v'][0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    return None

# Function to fetch the thumbnail URL of a YouTube video
def get_youtube_thumbnail_from_url(video_url):
    video_id = get_video_id_from_url(video_url)
    if video_id:
        return get_high_resolution_thumbnail(video_id)
    else:
        return None
   

def choice_query_category():
  return Category.query 


def choice_query_course():
  return Course.query.filter_by(author = current_user) 


