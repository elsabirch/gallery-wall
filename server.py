
from flask import (Flask, render_template, jsonify, url_for,
                   request, redirect, flash, session)
from jinja2 import StrictUndefined
from flask.ext.uploads import UploadSet, IMAGES, configure_uploads

from model import User, Picture, Gallery, Wall, Placement, connect_to_db, db

import settings
import secrets

import arrange as ar
import utilities as ut

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "notforyou"

# Jinja should not fail silently
app.jinja_env.undefined = StrictUndefined

# Configurations for flask-uploads
# These are required
app.config['UPLOADED_PICTURES_DEST'] = 'upload_temp'
pictures = UploadSet('pictures', IMAGES)
configure_uploads(app, (pictures,))
# These are a handy place to pass the info
app.config['S3_FOLDER'] = 'pictures'
app.config['S3_BUCKET'] = 'gallerywallshakedown'

# Configure paths for online resources
app.config['JQUERY_PATH'] = settings.jquery_path
app.config['BOOSTRAP_CSS_PATH'] = settings.boostrap_css_path
app.config['BOOSTRAP_JS_PATH'] = settings.boostrap_js_path
app.config['CHARTJS_PATH'] = settings.chartjs_path

# Default user ID used to display sample images when no other user logged in
DEFAULT_USER_ID = 1


@app.route('/')
def index():
    """Homepage."""

    # if 'user_id' in session:
    #     return redirect('/navigation')
    # else:
    return render_template("homepage.html")


@app.route('/navigation')
def navigation():
    """Navigate to various functional pages after login/guest."""

    return render_template("navigation.html")


@app.route('/login')
def prompt_login():
    """Page displaying forms to log in or sign up as user."""

    return render_template("login.html")


@app.route('/login-process', methods=['POST'])
def process_login():
    """Handle form submission for login process."""

    login_success = ut.attempt_login()

    if login_success:
        flash('Welcome {}!'.format(session['username']))
        return redirect('/navigation')

    else:
        flash("Something about that login attempt was invalid.")
        return redirect('/login')


@app.route('/signup-process', methods=['POST'])
def process_signup():
    """Handle form submission for signup process."""

    signup_success = ut.attempt_signup()

    if signup_success:
        flash("Sign up successful! Now log in.")
        return redirect('/login')

    else:
        flash("Something about that login attempt was invalid.")
        return redirect('/login')


@app.route('/logout-process')
def process_logout():
    """Handle form submission for logout process."""

    session.pop('user_id', None)
    session.pop('username', None)

    # flash message: logout successs
    flash("Successful log out. Goodbye!")
    return redirect('/')


@app.route('/upload')
def input_upload():

    return render_template('upload.html')


@app.route('/upload-process', methods=["POST"])
def process_upload():

    upload_success = ut.attempt_upload()

    if upload_success:
        flash('Image sucsessfully uploaded!')
        return redirect('/curate')

    else:
        flash('Something about the upload did not work.')
        return redirect('/upload')


@app.route('/curate')
def show_pictures():

    user_id = session.get('user_id', None)
    pictures = User.query.get(user_id).pictures
    pictures_public = db.session.query(Picture).filter(Picture.user_id != user_id,
                                           Picture.public == True).all()

    all_pictures = pictures + pictures_public

    return render_template('curate.html', user_pictures=all_pictures)


@app.route('/process-curation', methods=["POST"])
def process_curation():

    curate_success = ut.attempt_curation()

    if curate_success:
        return redirect('/galleries')
    else:
        flash('Cannot create empty gallery.')
        return redirect('/curate')


@app.route('/galleries')
def show_galleries():
    """Show a user's galleries that they can choose to arrange."""

    user_id = session.get('user_id', DEFAULT_USER_ID)
    galleries = User.query.get(user_id).galleries

    return render_template("galleries.html",
                           galleries=galleries)


@app.route('/arrange', methods=["GET"])
def prompt_arrangment():
    """Allow a user to input parameters about wall generation from gallery."""

    gallery_id = request.args.get('gallery_id')
    gallery = Gallery.query.get(gallery_id)

    # This is a get request because it does not have side effects, but check
    # they are the curator of this gallery or that it is site sample.
    if gallery.curator_id not in [session.get('user_id'), DEFAULT_USER_ID]:
        flash("That gallery doesnt exist or you don't have permission to view it.")
        return redirect('/galleries')

    arrange_options = ut.get_arrange_options_for_display()

    return render_template("arrange.html",
                           gallery=gallery,
                           arrange_options=arrange_options,
                           )


@app.route('/walls')
def show_walls():
    """Show a user's walls that they have arranged and saved."""

    user_id = session.get('user_id', DEFAULT_USER_ID)

    wall_ids = (db.session.query(Wall.wall_id)
                          .join(Gallery, User)
                          .filter(User.user_id == user_id,
                                  Wall.saved == True)
                          .order_by(Wall.wall_id.desc())
                          .all())
    # output is a list of tuples of ids
    wall_ids = [w[0] for w in wall_ids]

    return render_template("walls.html", wall_ids=wall_ids)


@app.route('/wall-dimensions', methods=["GET"])
def show_wall_dimensions():
    """Shows page with wall and table of hanging demensions."""

    wall_id = int(request.args.get('wall_id'))
    wall = Wall.query.get(wall_id)
    placements = wall.placements

    return render_template('wall-dimensions.html',
                           wall=wall,
                           placements=placements)


@app.route('/time')
def show_time():
    """For display of time tracked durring project."""

    return render_template('time-spark.html')

# Routes returning json data


@app.route('/save-wall.json', methods=["POST"])
def save_wall():
    """Changes the state of the wall in the database to saved."""

    wall_id = int(request.form.get('wall_id'))
    Wall.query.get(wall_id).save()
    Wall.query.get(wall_id).print_seed()

    return jsonify({'wall_id': wall_id})


@app.route('/getwall.json')
def get_wall_data():
    """Get the information needed for displaying a wall.

    Response to an AJAX request.
    """

    wall_id = request.args.get('wallid')
    wall = Wall.query.get(wall_id)

    if wall:
        wall_to_hang = wall.get_hanging_info()
    else:
        wall_to_hang = {'id': None}

    return jsonify(wall_to_hang)


@app.route('/getgallery.json')
def get_gallery_data():
    """Get the information needed for displaying a gallery.

    Response to an AJAX request.
    """

    gallery_id = request.args.get('galleryid')
    gallery = Gallery.query.get(gallery_id)

    if gallery:
        gallery_to_hang = gallery.get_display_info()
    else:
        gallery_to_hang = {'id': None}

    return jsonify(gallery_to_hang)


@app.route('/arrange.json', methods=['POST'])
def get_arranged_data():
    """Get the information needed for displaying a gallery.

    Response to an AJAX request.
    """

    gallery_id = int(request.form.get('gallery_id'))
    # margin = request.form.get('margin')
    wkspc = ar.Workspace(gallery_id)

    algorithm_type = request.form.get('algorithm_type')

    if algorithm_type == 'linear':
        arr = ar.LinearArranger(wkspc)
    elif algorithm_type == 'column':
        arr = ar.ColumnArranger(wkspc)
    elif algorithm_type == 'grid':
        arr = ar.GridArranger(wkspc)
    else:
        # Default to column arrangement
        arr = ar.ColumnArranger(wkspc)

    arr.arrange()

    wall_id = Wall.init_from_workspace(wkspc)

    new_wall_data = {'id': wall_id}

    return jsonify(new_wall_data)


@app.route('/gettime.json')
def get_time_data():
    """Get data from time tracking file."""

    from timetrack.time_track import get_time_spark

    plots = get_time_spark()

    return jsonify(plots)

if __name__ == "__main__":
    # Use debug mode
    app.debug = True

    connect_to_db(app)

    app.run()
