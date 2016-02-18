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
        self.n = len(pictures)

        self.pics = {}

        for picture in pictures:

            self.pics[picture.picture_id] = Pic(picture=picture,
                                                margin=self.margin)


        # Because it is common to need the largest, tallest, smallest, etc,
        # prepare these ahead fo time for the workspace
        self.area_sort = sorted([self.pics[p].id for p in self.pics],
                                key=lambda x: self.pics[x].a)
        self.width_sort = sorted([self.pics[p].id for p in self.pics],
                                key=lambda x: self.pics[x].w)
        self.height_sort = sorted([self.pics[p].id for p in self.pics],
                                key=lambda x: self.pics[x].h)


    def arrange_grid(self):
        """Arrangment via an initial placement in a grid."""

        pics_in_grid = self.random_place_in_grid()

        self.expand_grid_to_arrangment(pics_in_grid)

    def expand_grid_to_arrangment(self, pics_in_grid):
        """From a set of grid indicies produce geometrically valid placements.

        (grid = relative psuedo locations without geometry)"""
        # print '*'*80
        grid_ordered = sorted(pics_in_grid.keys())
        cols, rows = zip(*grid_ordered)
        max_i = max(cols)

        # for column # start in the middle
            # for i in range(0)
            # for row # start in the middle

            #  if at the center just place it (consider detect even number)

            # if grid neighbor above/below place at that vertical level

            # if can move towards center do that

    def arrange_column_heuristic(self):
        """Arrange in columns by a few rules."""

        # column = {'type': None,
        #             'width': 0,
        #             'height': 0,
        #             'pics': {}
        # }

        pics_remaining = set(self.pics.keys())

        # Create a column with the single tallest picture
        tallest = sorted([(self.pics[p]['height_mar'], p) for p in pics_remaining])[-1][1]
        # print(Picture.query.get(tallest))
        columns.append[ {'type': 'tall',
                  'width': self.pics[tallest]['width_mar'],
                  'height': self.pics[tallest]['height_mar'],
                  'pics': {tallest: [0, 0]}
                  }]
        pics_remaining.remove(tallest)
       
        # Create a column with wide pic and two skinny ones
        sorted_by_width = sorted([(self.pics[p]['width_mar'], p) for p in pics_remaining])

        widest = sorted_by_width[-1][1]
        # Consider getting these not as the skinniest but in general low end of dist
        skinny1 = sorted_by_width[0][1]
        skinny2 = sorted_by_width[1][1]

        pair_width = (self.pics[skinny1]['width_mar'] +
                      self.pics[skinny2]['width_mar'])
        single_width = self.pics[widest]['width_mar']

        # if pair_width => single_width:
        #     # pair is wider

        # else:
        #     pass

        # print(Picture.query.get(tallest))
        # columns.append[ {'type': 'nested',
        #           'width': self.pics[widest]['width_mar'],
        #           'height': self.pics[tallest]['height_mar'],
        #           'pics': {tallest: [0, 0]}
        #           }]

    def random_place_in_grid(self):
        """Place pics in random grid indicies.

        Returns a dict of tuple keys of grid indicies with pic id values
        {(i,j): pic}
        """

        n_pics = len(self.pics)
        n_grid = int(math.ceil(math.sqrt(n_pics)))
        min_grid = -n_grid/2
        max_grid = min_grid + n_grid

        grid_pairs = [(i, j) for i in range(min_grid, max_grid) 
                             for j in range(min_grid, max_grid)]

        grid_sample = random.sample(grid_pairs, n_pics)

        grid_pics = {grid_sample[i]:pic for i, pic in enumerate(self.pics.keys())}

        return grid_pics

    def arrange_linear(self):
        """Arrange gallery pictures in horizontal line, vertically centered."""

        mid_index = self.n / 2
        smaller_pics = self.area_sort[:mid_index]
        larger_pics = self.area_sort[mid_index:]
        random.shuffle(smaller_pics)
        random.shuffle(larger_pics)

        row_width = 0

        for i in range(len(self.pics)):
            p = smaller_pics.pop() if (i % 2 == 0) else larger_pics.pop()
            self.pics[p].x1 = row_width
            self.pics[p].x2 = row_width + self.pics[p].w
            self.pics[p].y1 = -self.pics[p].h / 2.0
            self.pics[p].y2 = self.pics[p].h + self.pics[p].y1

            row_width = self.pics[p].x2

    def realign_to_origin(self):
        """Shift all placements to positive quadrant with origin upper left."""

        x1s = [self.pics[p].x1 for p in self.pics]
        y1s = [self.pics[p].y1 for p in self.pics]

        x_shift = -min(x1s)
        y_shift = -min(y1s)

        for pic in self.pics:
            self.pics[pic].x1 += x_shift
            self.pics[pic].x2 += x_shift
            self.pics[pic].y1 += y_shift
            self.pics[pic].y2 += y_shift

    def get_wall_size(self):
        """Assgins as attributes the total wall height and width."""

        x1s = [self.pics[p].x1 for p in self.pics]
        x2s = [self.pics[p].x2 for p in self.pics]
        y1s = [self.pics[p].y1 for p in self.pics]
        y2s = [self.pics[p].y2 for p in self.pics]

        # If already adjusted to origin the second term of each expression is unnecesary
        self.width = max(x2s) - min(x1s)
        self.height = max(y2s) - min(y1s)

    def produce_placements(self):
        """Convert coordinates: remove rounding and margins used for placement."""

        self.placements = {}

        for p in self.pics:
            self.pics[p].picture
            self.placements[p] = {}
            width_fine = (math.ceil(self.pics[p].picture.width) - self.pics[p].picture.width) / 2
            height_fine = (math.ceil(self.pics[p].picture.height) - self.pics[p].picture.height) / 2
            self.placements[p]['x'] = self.pics[p].x1 + self.margin/2 + width_fine
            self.placements[p]['y'] = self.pics[p].y1 + self.margin/2 + height_fine


class Pic(object):
    """Pics are a data transfer object for placement genertion for pictures.

    Pics provide easy access and manuipulation durring arrangment to a
    subset and modification of pictures."""

    def __init__(self, picture, margin):
        """Initialize a pic with information from the picture and workspace."""

        self.id = picture.picture_id
        self.picture = picture

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

        self.w = int(math.ceil(picture.width)) + margin
        self.h = int(math.ceil(picture.height)) + margin

        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None

        self.a = self.w * self.h

# Functions

def arrange_gallery_1(gallery_id, arrange_options):
    """Calls methods in order for arrangment steps - shakedown testing. """

    # Instantiates object for working on the arrangment
    wkspc = Workspace(gallery_id, arrange_options)

    # This call creates the arrangment itself, will eventually have various
    # functions availible passed in options
    wkspc.arrange_linear()
    # wkspc.arrange_grid()
    # wkspc.arrange_column_heuristic()

    # These calls readjust the workspace to the origin, calculate precise
    # placments for wall hanging, and save other information for display
    wkspc.realign_to_origin()
    wkspc.get_wall_size()
    wkspc.produce_placements()

    return [wkspc.placements, wkspc.width, wkspc.height]
