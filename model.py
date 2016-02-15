"""Models and database functions for Gallery Wall project."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Picture(db.Model):
    """Picture to be included in gallery walls."""

    __tablename__ = "pictures"

    picture_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    width = db.Column(db.Float(), nullable=False)
    height = db.Column(db.Float(), nullable=False)
    public = db.Column(db.Boolean(), nullable=False, default=False)

    image_file = db.Column(db.String(400), nullable=True)
    # TODO: set user + name unique?
    picture_name = db.Column(db.String(100), nullable=True)
    image_attribution = db.Column(db.String(400), nullable=True)

    image_analyzed = db.Column(db.Boolean(), nullable=False, default=False)
    mat_fraction = db.Column(db.Float(), nullable=True)
    frame_code = db.Column(db.String(25), nullable=True)
    # TODO: add colors

    # Relationships
    galleries = db.relationship("Gallery",
                                secondary="gallery_memberships",
                                order_by="Gallery.gallery_id")
    user = db.relationship("User")

    def __repr__(self):
        """Representation format for output."""
        if self.picture_name:
            return "<{}: {:f} x {:f}>".format(self.picture_name,
                                              self.width,
                                              self.height)
        else:
            return "<Picture {:d}: {:f} x {:f}>".format(self.picture_id,
                                                        self.width,
                                                        self.height)


class GalleryMembership(db.Model):
    """Association table between pictures and galleries."""

    __tablename__ = "gallery_memberships"

    membership_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    gallery_id = db.Column(db.Integer, db.ForeignKey('galleries.gallery_id'))
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.picture_id'))

    # TODO link pictures and galliers through these

    def __repr__(self):
        """Representation format for output."""

        return "<Picture {} is a member of Gallery {}>".format(self.picture_id,
                                                               self.gallery_id)


class Gallery(db.Model):
    """Gallery is an unordered set of pictures to be arranged."""

    __tablename__ = "galleries"

    gallery_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # TODO: set user + name unique? if users
    gallery_name = db.Column(db.String(100), nullable=True)

    curator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    # Relationships
    pictures = db.relationship("Picture",
                               secondary="gallery_memberships",
                               order_by="desc(Picture.height)")
    walls = db.relationship("Wall", order_by="Wall.wall_id")

    def get_display_info(self):
        """Creates dictionary analogous to that for walls, for jsonification.

        Pictures displayed by descending height.

        NOTE: ASSUMES THAT PICTURES REALTIONSHIP OUTPUTS DESCENDING HEIGHT.
        """

        margin = 2

        total_width = sum([p.width for p in self.pictures])
        gallery_width = (total_width / 2.0) + (total_width / len(self.pictures))

        gallery_height = margin + self.pictures[0].height
        current_row_width = margin
        current_row_top = margin

        pictures_to_hang = {}

        # Hang pictures in rows
        for picture in self.pictures:
            # Start a new row if this one is full
            if (current_row_width + picture.width) > gallery_width:
                current_row_top = gallery_height + margin
                gallery_height += picture.height + margin
                current_row_width = margin

            pictures_to_hang[picture.picture_id] = {
                'x': current_row_width,
                'y': current_row_top,
                'width': picture.width,
                'height': picture.height,
                'image': picture.image_file,
                }

            current_row_width += picture.width + margin

        hanging_info = {
                        'id': self.gallery_id,
                        'height': gallery_height + margin,
                        'width': gallery_width,
                        'pictures_to_hang': pictures_to_hang,
                        }

        return hanging_info

    def __repr__(self):
        """Representation format for output."""
        if self.gallery_name:
            return "<Gallery {}>".format(self.gallery_name)
        else:
            return "<Gallery ID {:d}>".format(self.gallery_id)


class Wall(db.Model):
    """Wall arrangment of pictures from a gallery."""

    __tablename__ = "walls"

    wall_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    gallery_id = db.Column(db.Integer, db.ForeignKey('galleries.gallery_id'))
    saved = db.Column(db.Boolean(), nullable=False, default=False)

    wall_width = db.Column(db.Float(), nullable=False)
    wall_height = db.Column(db.Float(), nullable=False)

    # Relationships
    gallery = db.relationship("Gallery")
    placements = db.relationship("Placement")

    def get_hanging_info(self):
        """Returns a dictionary containing the needed information for display."""

        pictures_to_hang = {}

        for placement in self.placements:
            pictures_to_hang[placement.picture_id] = {
                'x': placement.x_coord,
                'y': placement.y_coord,
                'width': placement.picture.width,
                'height': placement.picture.height,
                'image': placement.picture.image_file,
                }

        hanging_info = {
                        'id': self.wall_id,
                        'height': self.wall_height,
                        'width': self.wall_width,
                        'pictures_to_hang': pictures_to_hang,
                        }

        return hanging_info

    def __repr__(self):
        """Representation format for output."""

        return "<Wall {:d} of Gallery {:d}>".format(self.wall_id,
                                                    self.gallery.gallery_id)


class Placement(db.Model):
    """Location of a picture within a wall arrangment."""

    __tablename__ = "placements"

    placement_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    wall_id = db.Column(db.Integer, db.ForeignKey('walls.wall_id'))
    picture_id = db.Column(db.Integer, db.ForeignKey('pictures.picture_id'))

    # TODO: discuss numeric here? and UNITS!
    x_coord = db.Column(db.Float(), nullable=False)
    y_coord = db.Column(db.Float(), nullable=False)

    # Relationships
    wall = db.relationship("Wall")
    picture = db.relationship("Picture")

    def __repr__(self):
        """Representation format for output."""

        return "<Placement {:d} in Wall {:d} of Image {:d}>".format(
            self.placement_id, self.wall_id, self.picture.picture_id)


class User(db.Model):
    """User associated with pictures and their arangments."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.String(25), nullable=False, unique=True)

    galleries = db.relationship("Gallery", order_by="Gallery.gallery_id")
    pictures = db.relationship("Picture", order_by="Picture.picture_id")
    walls = db.relationship("Wall", secondary='galleries', order_by="Wall.wall_id")

    def __repr__(self):
        """Representation format for output."""

        return "<User {:d} Username {}>".format(self.user_id, self.username)

##############################################################################
# Helper functions


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///gallerywall'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
