"""Models and database functions for Gallery Wall project."""

from flask_sqlalchemy import SQLAlchemy
# import arrange

def lazy_load_of_workspace():
    print 'lazy loading'
    # global Workspace
    # global GalleryFloorArranger
    global ar
    import arrange as ar

    # from arrange import Workspace as _Workspace
    # from arrange import GalleryFloorArranger as _GalleryFloorArranger
    # Workspace = _Workspace
    # GalleryFloorArranger = _GalleryFloorArranger
    # import arrange as ar

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

    @property
    def display_name(self):
        """Property to provide the name if it exists and Id as a string if not."""

        if self.picture_name:
            return self.picture_name
        else:
            return "Id {:d}".format(self.picture_id)

    def __repr__(self):
        """Representation format for output."""

        return "<{}: {:f} x {:f}>".format(self.display_name,
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

    @property
    def test_prop(self):

        print 'I AM TEH PROPERTY OF GALLAREEEEEZ'
        return 'I AM TEH PROPERTY & I work'

    @property
    def display_wall_id(self):

        wall_id = (db.session.query(Wall.wall_id)
                             .join(Gallery)
                             .filter(Gallery.gallery_id == self.gallery_id,
                                     Wall.gallery_display == True)
                             .first())

        # wall_id = []

        if not wall_id:

            arrange_options = {}

            lazy_load_of_workspace()
            print 'making a workspace'
            wkspc = ar.Workspace(self.gallery_id)
            print 'made a workspace'
            arranger_instance = ar.GalleryFloorArranger(wkspc)
            print 'made a galelry arranger'
            # import pdb
            # pdb.set_trace()
            arranger_instance.arrange_x()
            print 'arranged that stuff'
            # wkspc.arrange_gallery_display_floor()
            wall_id = Wall.init_from_workspace(wkspc)
            db.session.flush()
            print 'i inited a wall'
            Wall.query.get(wall_id).set_gallery_display()

        else:
            # TODO: there should be a more graceful way to deal with that query
            # returning either None or a tuple
            wall_id = wall_id[0]

        return wall_id


    @classmethod
    def make_from_pictures(cls, curator_id, picture_list, gallery_name=None):

        gallery = Gallery(gallery_name=gallery_name,
                          curator_id=curator_id)

        db.session.add(gallery)
        db.session.flush()

        # TODO: Check that all pictures belong to user or are public

        # Store memberships in database
        for picture_id in picture_list:
            membership = GalleryMembership(gallery_id=gallery.gallery_id,
                                           picture_id=picture_id)
            db.session.add(membership)
        db.session.commit()

        return gallery

    def print_seed(self):
        """Print the seed format of a gallery to save as a sample."""

        print '-'*20 + 'Memberships Entry' + '-'*20

        # gallery_id | picture_id, picture_id, ...

        pictures_str = [str(p.picture_id) for p in self.pictures]

        print '{:d} | {:s}'.format(self.gallery_id, ', '.join(pictures_str))

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

    gallery_display = db.Column(db.Boolean(), nullable=False, default=False)

    # Relationships
    gallery = db.relationship("Gallery")
    placements = db.relationship("Placement")

    @classmethod
    def init_from_workspace(cls, workspace):
        """Initialize a wall and the related placements from a workspace."""

        wall = cls(gallery_id=workspace.gallery_id,
                   wall_width=workspace.width,
                   wall_height=workspace.height,
                   )
        db.session.add(wall)
        db.session.flush()

        wall_id = wall.wall_id

        # Store placements in database
        for pic_id in workspace.pics:
            placement = Placement(wall_id=wall_id,
                                  picture_id=pic_id,
                                  x_coord=workspace.pics[pic_id].x1,
                                  y_coord=workspace.pics[pic_id].y1)

            db.session.add(placement)
        db.session.commit()

        return wall_id

    def save(self):
        """Sets wall state to saved."""

        self.saved = True

        db.session.commit()

    def set_gallery_display(self):
        """Sets wall flag for gallery display."""

        self.gallery_display = True

        db.session.commit()

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
                        'is_gallery': self.gallery_display,
                        }

        return hanging_info


    def print_seed(self):
        """Print the seed format of a wall to save as a sample."""

        print '-'*20 + 'Wall Entry' + '-'*20

        # wall_id | gallery_id | wall_width | wall_height | saved
        print ' | '.join(['{:d}'.format(self.wall_id),
                          '{:d}'.format(self.gallery.gallery_id),
                          '{:0.2f}'.format(self.wall_width),
                          '{:0.2f}'.format(self.wall_height),
                          'True',
                          ])

        print '-'*20 + 'Placement Entries' + '-'*20

        for placement in self.placements:
            # wall_id | picture_id | x | y
            print ' | '.join(['{:d}'.format(self.wall_id),
                              '{:d}'.format(placement.picture_id),
                              '{:0.2f}'.format(placement.x_coord),
                              '{:0.2f}'.format(placement.y_coord),
                              ])

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
