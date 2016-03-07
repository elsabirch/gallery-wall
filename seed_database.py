
from sqlalchemy import func

from model import User, Picture, GalleryMembership, Gallery, Wall, Placement
from model import connect_to_db, db

from server import app


def load_users():
    """Add users to database from text file.

    Data file is pipe seperated:
    username | email | password
    """

    # If seeding database clear previous data out
    # User.query.delete()

    # query = "ALTER SEQUENCE users_user_id_seq RESTART"
    # db.session.execute(query)
    # db.session.commit()

    with open("seed/seed_users.txt") as seed_file:
        for line in seed_file:
            username, email, password = line.rstrip().split("|")

            username = username.strip()
            email = email.strip()
            password = password.strip()

            user = User(username=username,
                        email=email,
                        password=password)

            db.session.add(user)

        db.session.commit()


def load_pictures():
    """Add sample pictures to database from text file.

    Data file is pipe seperated:
    picture_id | user_id | width | height | image_file |
        picture_name | image_attribution | public
    """

    # If seeding database clear previous data out
    # Picture.query.delete()

    seed_image_folder_path = "static/img_samples/"

    with open("seed/seed_pictures.txt") as seed_file:
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


def load_galleries():
    """Add sample galleries to database from text file.

    Data file is pipe seperated:
    gallery_id | gallery_name | curator_id
    """

    with open("seed/seed_galleries.txt") as seed_file:
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

def load_memberships():
    """Add sample pictures to galleries in database from text file.

    Data file is pipe seperated, with comma seperated list of pictures:
    gallery_id | picture_id, picture_id, ...
    """

    with open("seed/seed_memberships.txt") as seed_file:
        for line in seed_file:
            gallery_id, comma_sep_pictures = line.rstrip().split("|")

            pictures = comma_sep_pictures.split(",")

            for picture in pictures:
                picture_id = int(picture)

                membership = GalleryMembership(gallery_id=gallery_id,
                                               picture_id=picture_id)

                db.session.add(membership)

        db.session.commit()


def load_walls():
    """Add sample walls to database from text file.

    Data file is pipe seperated:
    wall_id | gallery_id | wall_width | wall_height | saved
    """

    with open("seed/seed_walls.txt") as seed_file:
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

def load_placements():
    """Add sample walls to database from text file.

    Data file is pipe seperated:
    wall_id | picture_id | x | y
    """

    with open("seed/seed_placements.txt") as seed_file:
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

def prepare_all():
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.drop_all()
    db.create_all()
    print "Database droped & created!"

    # Import different types of data
    load_users()
    load_pictures()
    load_galleries()
    load_memberships()
    load_walls()
    load_placements()    

if __name__ == "__main__":
    
    prepare_all()

