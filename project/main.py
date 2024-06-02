from flask import (
  Blueprint, render_template, request, 
  flash, redirect, url_for, send_from_directory, 
  current_app, make_response
)
from .models import Photo, Comments, Album
from sqlalchemy import asc, text
from . import db
import os
#import logger

main = Blueprint('main', __name__)

# This is called when the home page is rendered. It fetches all images sorted by filename.
@main.route('/')
def homepage():
  photos = db.session.query(Photo).order_by(asc(Photo.file))
  return render_template('index.html', photos = photos)

@main.route('/uploads/<name>')
def display_file(name):
  return send_from_directory(current_app.config["UPLOAD_DIR"], name)

# Upload a new photo
@main.route('/upload/', methods=['GET','POST'])
def newPhoto():
  if request.method == 'POST':
    file = None
    if "fileToUpload" in request.files:
      file = request.files.get("fileToUpload")
    else:
      flash("Invalid request!", "error")

    if not file or not file.filename:
      flash("No file selected!", "error")
      return redirect(request.url)

    filepath = os.path.join(current_app.config["UPLOAD_DIR"], file.filename)
    file.save(filepath)

    newPhoto = Photo(name = request.form['user'], 
                    caption = request.form['caption'],
                    description = request.form['description'],
                    file = file.filename)
    db.session.add(newPhoto)
    flash('New Photo %s Successfully Created' % newPhoto.name)
    db.session.commit()
    return redirect(url_for('main.homepage'))
  else:
    return render_template('upload.html')

# This is called when clicking on Edit. Goes to the edit page.
@main.route('/photo/<int:photo_id>/edit/', methods = ['GET', 'POST'])
def editPhoto(photo_id):
  editedPhoto = db.session.query(Photo).filter_by(id = photo_id).one()
  if request.method == 'POST':
    if request.form['user']:
      editedPhoto.name = request.form['user']
      editedPhoto.caption = request.form['caption']
      editedPhoto.description = request.form['description']
      db.session.add(editedPhoto)
      db.session.commit()
      flash('Photo Successfully Edited %s' % editedPhoto.name)
      return redirect(url_for('main.homepage'))
  else:
    return render_template('edit.html', photo = editedPhoto)


# This is called when clicking on Delete. 
@main.route('/photo/<int:photo_id>/delete/', methods = ['GET','POST'])
def deletePhoto(photo_id):
  fileResults = db.session.execute(text('select file from photo where id = ' + str(photo_id)))
  filename = fileResults.first()[0]
  filepath = os.path.join(current_app.config["UPLOAD_DIR"], filename)
  os.unlink(filepath)
  db.session.execute(text('delete from photo where id = ' + str(photo_id)))
  db.session.commit()
  
  flash('Photo id %s Successfully Deleted' % photo_id)
  return redirect(url_for('main.homepage'))

#New Features - Comments
@main.route('/photo/<int:id>/comments/', methods=['GET'])
def viewComments(id):
    photo = Photo.query.get(id)
    comments = Comments.query.get(id)
    sanitizedComments = [{'id': c.id, 'user_id': c.user_id, 'text': c.text, 'timestamp': c.timestamp} for c in comments]
    # sanitized the comments to try and prevent XSS
    return sanitizedComments

@main.route('/photo/<int:id>/comments/add/', methods=['POST'])
#@logintrue
def addComment(id):
    photo = Photo.query.get(id)
    text = request.form.get('text')
    if not text or len(text) > 20:
      flash('Invalid comment')
      # input validation for if there is no comment or its too long
      return redirect(url_for('view_comments', id=id))
    sanitized_text = text.replace('<', '&lt;').replace('>', '&gt;')
    #sanitized for inputs to try and stop XSS
    new_comment = Comments(photo_id=id, user_id=user.id, text=sanitized_text)
    db.session.add(new_comment)
    db.session.commit()
    logger.info(f'Comment added to photo {id} by user {user.id}')
    #logging who made the comment
    flash('Comment added')
    return redirect(url_for('view_comments', id=id))

@main.route('/photo/<int:photo_id>/comments/<int:comment_id>/delete/', methods=['POST'])
#logintrue
def deleteComment(photo_id, comment_id):
    comment = Comments.query.get(id)
    if user.id != Comments.user_id and not user.is_admin:
        flash('No permission')
        # Auth check for admin or owner
        return redirect(url_for('view_comments', id=photo_id))
    db.session.delete(comment)
    db.session.commit()
    logger.info(f'Comment {comment_id} deleted from photo {photo_id} by user {user.id}')
    #logging who deleted it
    flash('Comment deleted')
    return redirect(url_for('view_comments', id=photo_id))

# new Feature Album
@main.route('/album/<int:a_id>', methods=['GET'])
def viewAlbum(a_id):
    album = Album.query(a_id)
    sanitized_album = {
        'id': album.id,
        'name': album.name.replace('<', '&lt;').replace('>', '&gt;'),  
        'photos': [{'id': p.id, 'file': p.file, 'caption': p.caption.replace('<', '&lt;').replace('>', '&gt;')} for p in album.photos]  
        # sanitize the alumns name
    }
    return sanitized_album

@main.route('/album/create/', methods=['POST'])
#logintrue
def createAlbum():
    name = request.form.get('name')
    if not name or len(name) > 20:
        flash('Invalid name')
        # validating that the name is there and not too long
        return redirect(url_for('view_album', a_id=new_album.id))
    sanitized_name = name.replace('<', '&lt;').replace('>', '&gt;') 
     # sanitizing the name for xss
    new_album = Album(name=sanitized_name, user_id=user.id)
    db.session.add(new_album)
    db.session.commit()
    logger.info(f'Album {new_album.id} created by user {user.id}')
    #logging who made the album
    flash('Album made')
    return redirect(url_for('view_album', a_id=new_album.id))

@main.route('/album/<int:a_id>/add/', methods=['POST'])
#logintrue
def addPhotoToAlbum(a_id):
    album = Album.query.get(a_id)
    if album.user_id != user.id:
        flash('No permission')
        # Auth check to see if album owner
        return redirect(url_for('view_album', a_id=a_id))
    photo_id = request.form.get('photo_id')
    photo = Photo.query.get(photo_id)
    photo.album_id = a_id
    db.session.commit()
    logger.info(f'Photo {photo_id} added to album {a_id} by user {user.id}')
    # logging to see who did it
    flash('Photo added')
    return redirect(url_for('view_album', a_id=a_id))

# Delete Album
@main.route('/album/<int:a_id>/delete/', methods=['POST'])
#logintrue
def delete_album(a_id):
    album = Album.query.get(a_id)
    if user.id != album.user_id and not user.is_admin:
        flash('No permission')
        # auth check for admin or owner
        return redirect(url_for('view_album', a_id=a_id))
    db.session.delete(album)
    db.session.commit()
    logger.info(f'Album {a_id} deleted by user {user.id}')
    # logged to see who did it
    flash('Album deleted')
    return redirect(url_for('homepage'))