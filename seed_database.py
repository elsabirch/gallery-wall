
from sqlalchemy import func

from model import User, Picture, GalleryMembership, Gallery, Wall, Placement
from model import connect_to_db, db

from server import app


def load_users(seed_file_path):
    """Add users to database from text file.

    Data file is pipe seperated:
    user_id | username | email | password
    """

    with open(seed_file_path) as seed_file:
        for line in seed_file:
            user_id, username, email, password = line.rstrip().split("|")

            user_id = int(user_id)
            username = username.strip()
            email = email.strip()
            password = password.strip()

            user = User(
                user_id=user_id,
                username=username,
                email=email,
                password=password
                )

            db.session.add(user)

        db.session.commit()

    # Reset seq/counter
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])
    query = "ALTER SEQUENCE users_user_id_seq RESTART WITH :next_id"
    db.session.execute(query, {'next_id': max_id+1})
    db.session.commit()


def load_pictures(seed_file_path):
    """Add sample pictures to database from text file.

    Data file is pipe seperated:
    picture_id | user_id | width | height | image_file |
        picture_name | image_attribution | public
    """

    seed_image_folder_path = "static/img_samples/"

    with open(seed_file_path) as seed_file:
        for line in seed_file:
            tokens = line.rstrip().split("|")

            picture_id = int(tokens[0])
            user_id = int(tokens[1])
            width = float(tokens[2])
            height = float(tokens[3])
            image_raw = tokens[4].strip()
            image_file = (seed_image_folder_path + image_raw) if image_raw else None
            picture_name = tokens[5].strip()
            image_attribution = tokens[6].strip()
            public = tokens[7].strip().lower() == 'public'

            picture = Picture(picture_id=picture_id,
                              user_id=user_id,
                              width=width,
                              height=height,
                              image_file=image_file,
                              picture_name=picture_name,
                              image_attribution=image_attribution,
                              public=public,
                              )

            db.session.add(picture)

        db.session.commit()

    # Reset seq/counter
    result = db.session.query(func.max(Picture.picture_id)).one()
    max_id = int(result[0])
    query = "ALTER SEQUENCE pictures_picture_id_seq RESTART WITH :next_id"
    db.session.execute(query, {'next_id': max_id+1})
    db.session.commit()


def load_galleries(seed_file_path):
    """Add sample galleries to database from text file.

    Data file is pipe seperated:
    gallery_id | gallery_name | curator_id
    """

    with open(seed_file_path) as seed_file:
        for line in seed_file:
            gallery_id, gallery_name, curator_id = line.rstrip().split("|")

            # Currently gallery_id is discarded
            gallery_name = gallery_name.strip()
            curator_id = int(curator_id)

            gallery = Gallery(
                gallery_id=gallery_id,
                gallery_name=gallery_name,
                curator_id=curator_id,
                )

            db.session.add(gallery)

        db.session.commit()

    result = db.session.query(func.max(Gallery.gallery_id)).one()
    max_id = int(result[0])
    query = "ALTER SEQUENCE galleries_gallery_id_seq RESTART WITH :next_id"
    db.session.execute(query, {'next_id': max_id+1})
    db.session.commit()


def load_memberships(seed_file_path):
    """Add sample pictures to galleries in database from text file.

    Data file is pipe seperated, with comma seperated list of pictures:
    gallery_id | picture_id, picture_id, ...
    """

    with open(seed_file_path) as seed_file:
        for line in seed_file:
            gallery_id, comma_sep_pictures = line.rstrip().split("|")

            pictures = comma_sep_pictures.split(",")

            for picture in pictures:
                picture_id = int(picture)

                membership = GalleryMembership(gallery_id=gallery_id,
                                               picture_id=picture_id)

                db.session.add(membership)

        db.session.commit()


def load_walls(seed_file_path):
    """Add sample walls to database from text file.

    Data file is pipe seperated:
    wall_id | gallery_id | wall_width | wall_height | saved
    """

    with open(seed_file_path) as seed_file:
        for line in seed_file:
            wall_id, gallery_id, wall_width, wall_height, saved = line.rstrip().split("|")

            # Currently gallery_id is discarded
            wall_id = int(wall_id)
            gallery_id = int(gallery_id)
            wall_width = int(wall_width)
            wall_height = int(wall_height)
            saved = saved.strip().lower() == 'saved'

            wall = Wall(wall_id=wall_id,
                        gallery_id=gallery_id,
                        wall_width=wall_width,
                        wall_height=wall_height,
                        saved=saved)

            db.session.add(wall)

        db.session.commit()

    # Reset counter
    result = db.session.query(func.max(Wall.wall_id)).one()
    max_id = int(result[0])
    query = "ALTER SEQUENCE walls_wall_id_seq RESTART WITH :next_id"
    db.session.execute(query, {'next_id': max_id+1})
    db.session.commit()


def load_placements(seed_file_path):
    """Add sample walls to database from text file.

    Data file is pipe seperated:
    wall_id | picture_id | x | y
    """

    with open(seed_file_path) as seed_file:
        for line in seed_file:
            wall_id, picture_id, x_coord, y_coord = line.rstrip().split("|")

            # Currently gallery_id is discarded
            wall_id = int(wall_id)
            picture_id = int(picture_id)
            x_coord = float(x_coord)
            y_coord = float(y_coord)

            placement = Placement(wall_id=wall_id,
                                  picture_id=picture_id,
                                  x_coord=x_coord,
                                  y_coord=y_coord)

            db.session.add(placement)

        db.session.commit()


def clean_db():

    # In case tables haven't been created, create them
    db.session.commit()
    db.drop_all()
    db.create_all()


def seed_all(seed_files):

    # Import different types of data
    load_users(seed_files['users'])
    load_pictures(seed_files['pictures'])
    load_galleries(seed_files['galleries'])
    load_memberships(seed_files['memberships'])
    load_walls(seed_files['walls'])
    load_placements(seed_files['placements'])


if __name__ == "__main__":

    connect_to_db(app)

    clean_db()
    print "Database tables droped & created."

    seed_files = {
        'users': "seed/seed_users.txt",
        'pictures': "seed/seed_pictures.txt",
        'galleries': "seed/seed_galleries.txt",
        'memberships': "seed/seed_memberships.txt",
        'walls': "seed/seed_walls.txt",
        'placements': "seed/seed_placements.txt",
    }

    seed_all(seed_files)
    print "Tables seeded."
