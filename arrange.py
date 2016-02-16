from model import Picture, Gallery, Wall, Placement
import math
import random

DEFAULT_MARGIN = 2


class Workspace(object):
    """Class on which arrangments can be performed."""

    def __init__(self, gallery_id, options):
        """Constructor from picture list."""

        pictures = Gallery.query.get(gallery_id).pictures

        self.gallery_id = gallery_id
        self.margin = options.get('margin', DEFAULT_MARGIN)

        self.xs = []
        self.ys = []
        self.pics = {}

        for picture in pictures:
            pic = picture.picture_id
            self.pics[pic] = {}
            # Note, each side of each picture carries half the margin
            #
            #        w+m
            #     <------->
            #          w   m
            #       <----><->
            #     +--------+---------+
            #     | +----+ | +-----+ |
            #     | |    | | |     | |
            #     | +----+ | +-----+ |
            #     +--------+---------+
            #
            # Rounding here serves to avoid unnesesary treatment of fractional
            # gaps, and should simplify logic some.
            self.pics[pic]['width_mar'] = int(math.ceil(picture.width)) + self.margin
            self.pics[pic]['height_mar'] = int(math.ceil(picture.height)) + self.margin

            # self.xs.append([None, None, pic])
            # self.ys.append([None, None, pic])

    def get_area_queue(self):
        """Returns a list of margin padded picture areas, as tuples with id."""

        return [(self.pics[p]['width_mar'] * self.pics[p]['height_mar'], p)
                for p in self.pics]

    def arrange_linear(self):
        """Arrange gallery pictures in horizontal line, vertically centered."""

        # Use areas as a rough approximation for size to create alternating wall
        areas_with_id = sorted(self.get_area_queue())

        row_width = 0
        end_select = True

        while len(areas_with_id) > 0:
            # Use random integer to select an indiex from one or the other end
            # of the list
            i = random.randint(0, len(areas_with_id) / 2)
            index = i if end_select else (-(i + 1))

            pic = areas_with_id.pop(index)[1]

            x1 = row_width
            x2 = row_width+self.pics[pic]['width_mar']
            y1 = -self.pics[pic]['height_mar']/2
            y2 = self.pics[pic]['height_mar']-self.pics[pic]['height_mar']/2

            self.xs.append([x1, x2, pic])
            self.ys.append([y1, y2, pic])
            row_width = x2  #  + 1

    def realign_to_origin(self):
        """Shift all placements to positive quadrant with origin upper left."""

        x1s, x2s, pics = zip(*self.xs)
        y1s, y2s, pics = zip(*self.ys)

        x_shift = -min(x1s)
        y_shift = -min(y1s)

        self.xs = [[(z[0] + x_shift), (z[1] + x_shift), z[2]] for z in self.xs]
        self.ys = [[(z[0] + y_shift), (z[1] + y_shift), z[2]] for z in self.ys]

    def get_wall_size(self):
        """Assgins as attributes the total wall height and width."""

        x1s, x2s, pics = zip(*self.xs)
        y1s, y2s, pics = zip(*self.ys)

        # If already adjusted to origin the second term of each expression is unnecesary
        self.width = max(x2s) - min(x1s)
        self.height = max(y2s) - min(y1s)

    def produce_placements(self):
        """Convert coordinates: remove rounding and margins used for placement."""

        self.placements = {}

        # Note that the coordinate lists may NOT be in the same order, thus
        # convert to dicts so the pair for each can easily be retrieved
        pic_x1s = {z[2]: z[0] for z in self.xs}
        pic_y1s = {z[2]: z[0] for z in self.ys}

        for pic in pic_x1s:
            picture = Picture.query.get(pic)
            self.placements[pic] = {}
            # self.placements[pic]['x'] = (pic_x1s[pic] + self.margin/2 +
            #                              (1.0 - (picture.width % 1)) / 2)
            # self.placements[pic]['y'] = (pic_y1s[pic] + self.margin/2 +
            #                              (1.0 - (picture.height % 1)) / 2)
            self.placements[pic]['x'] = (pic_x1s[pic] + self.margin/2 +
                                         ((1.0 - (picture.width % 1) / 2) if (picture.width % 1) else 0))
            self.placements[pic]['y'] = (pic_y1s[pic] + self.margin/2 +
                                         ((1.0 - (picture.height % 1) / 2) if (picture.height % 1) else 0))
    
    # def add_wall_to_db(self):
    #     """Add the wall to the database, and get wall_id for placment saving."""

    #     wall = Wall(gallery_id=self.gallery_id,
    #                 wall_width=self.width,
    #                 wall_height=self.height,
    #                 )
    #     db.session.add(wall)
    #     db.session.commit()

    #     self.wall_id = wall.wall_id

    # def add_placements_to_db(self):
    #     pass

# Functions

def arrange_gallery_1(gallery_id, arrange_options):
    """Calls methods in order for arrangment steps - shakedown testing. """

    print "Arrangement call for gallery {}".format(gallery_id)

    wkspc = Workspace(gallery_id, {'margin': 2})

    wkspc.arrange_linear()
    wkspc.realign_to_origin()
    wkspc.get_wall_size()

    print wkspc.width
    print wkspc.height
    print wkspc.xs
    print wkspc.ys

    wkspc.produce_placements()

    return [wkspc.placements, wkspc.width, wkspc.height]
