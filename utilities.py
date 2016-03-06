from flask import session, request
from model import User, Picture, Gallery, db

import re
import random
import os
import boto3

def lazy_load_of_upload_imports():
    global pictures
    global app
    from server import pictures, app


def attempt_login():
    """Logs user into session and returns True if POST credentials valid.

    Otherwise returns False.
    """

    attempted_username = request.form.get('username').strip().lower()
    attempted_password = request.form.get('password')

    user = User.query.filter(User.username == attempted_username).first()

    if (user is None) or not attempted_username:
        # User was invalid, or empty to begin with
        return False

    elif attempted_password == user.password:
        # Credentials valid, add to session
        session['user_id'] = user.user_id
        session['username'] = user.username
        return True

    else:
        # Password was invalid
        return False


def attempt_signup():
    """Adds user into database and returns True if POST credentials valid.

    Otherwise returns False.
    """

    attempted_username = request.form.get('username').strip().lower()
    attempted_email = request.form.get('email')
    attempted_password = request.form.get('password')

    user = User.query.filter(User.username == attempted_username).first()

    if (user is None) and attempted_username:
        # User not already existing, and a username was entered
        user = User(username=attempted_username,
                    email=attempted_email,
                    password=attempted_password)
        db.session.add(user)
        db.session.commit()

        return True

    else:
        # User was invalid or nonexistant
        return False


def attempt_upload():

    lazy_load_of_upload_imports()

    filename_provided = pictures.save(request.files['picture'])

    width = to_float_from_input(request.form.get('width'))
    height = to_float_from_input(request.form.get('height'))
    name = to_clean_string_from_input(request.form.get('name'), 100)
    # TODO: Validate hight/width roughly match image, are positive and nonzero

    user_id = session.get('user_id', None)

    if filename_provided and width and height and user_id:

        picture = Picture(user_id=user_id, width=width, height=height)
        if name:
            picture.picture_name = name
        db.session.add(picture)
        db.session.flush()

        # Rename file after adding so that the picture_id can be used,
        # this may not really be neccesary to include in the file name.
        filename = rename_picture_on_server(filename_provided, picture.picture_id)
        url = move_picture_to_cloud(filename)
        picture.image_file = url
        db.session.commit()

        return True

    else:
        return False


def attempt_curation():
    """Creates gallery from POST request pictures and returns True is successful.

    Returns false otherwise."""

    user_id = session.get('user_id', None)

    picture_ids = [int(p) for p in request.form.getlist('gallery_member')]

    if len(picture_ids) > 0:
        gallery_name = to_clean_string_from_input(request.form.get('gallery_name'),
                                                  max_length=100)
        gallery = Gallery.make_from_pictures(curator_id=user_id,
                                             picture_list=picture_ids,
                                             gallery_name=gallery_name)
        # gallery.print_seed()
        return True
    else:
        return False

def get_arrange_options_for_display():
    """Returns a list of dicts with display information for the arrange page.

    This interface may be expanded into it's own class when more options exist.
    """

    arrange_options = [

        {
            'algorithm_type': 'linear',
            'display_name': 'Linear',
            'image': "/static/img/linear_icon.jpg",
            'description': "Scatter & center!",
        },

        {
            'algorithm_type': 'column',
            'display_name': 'Columner',
            'image': "/static/img/column_icon.jpg",
            'description': "Heuristics FTW!",
        },

        {
            'algorithm_type': 'grid',
            'display_name': 'Cloud-Like',
            'image': "/static/img/cloud_icon.jpg",
            'description': "Oh look a random walk!",
        },
    ]

    return arrange_options


def rename_picture_on_server(filename_provided, picture_id):
    """Rename picture using id and random number, returns new name."""

    extension = filename_provided[filename_provided.find('.'):]
    unpredictable = random.randint(100000, 999999)
    filename = 'picture{:d}_{:d}{:s}'.format(picture_id,
                                             unpredictable,
                                             extension)

    folder_server = app.config['UPLOADED_PICTURES_DEST']
    os.rename('{}/{}'.format(folder_server, filename_provided),
              '{}/{}'.format(folder_server, filename))

    return filename


def move_picture_to_cloud(filename):
    """Uploads file to s3, deletes from server, returns url for picture."""

    folder_server = app.config['UPLOADED_PICTURES_DEST']

    client = boto3.client('s3')
    transfer = boto3.s3.transfer.S3Transfer(client)

    transfer.upload_file('{}/{}'.format(folder_server, filename),
                         app.config['S3_BUCKET'],
                         '{}/{}'.format(app.config['S3_FOLDER'], filename),
                         extra_args={'ACL': 'public-read'})

    uploaded = '{}/{}/{}'.format(client.meta.endpoint_url,
                                 app.config['S3_BUCKET'],
                                 '{}/{}'.format(app.config['S3_FOLDER'], filename))

    os.remove('{}/{}'.format(folder_server, filename))

    return uploaded


def to_float_from_input(input_string):
    """From an input text string return the first float found otherwise None."""

    input_string.strip()

    match = re.search('(\-)?\d+(\.\d+)?', input_string)
    if match:
        return float(match.group(0))
    else:
        return


def to_clean_string_from_input(input_string, max_length):
    """Clean a string to only alphanumeric, and limit to input length.

    >>> to_clean_string_from_input('foo*', 10)
    'foo'

    """

    clean_string = re.sub('\W', '', input_string)
    if len(clean_string) >= max_length:
        clean_string = clean_string[:max_length]
    elif len(clean_string) == 0:
        clean_string = None

    return clean_string
