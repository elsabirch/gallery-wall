import math
import random

# Note: unable to import Gallery from model specifically because model imports arrange too
import model

DEFAULT_MARGIN = 2



class Workspace(object):
    """Class on which arrangments can be performed."""

    def __init__(self, gallery_id, options):
        """Constructor from picture list."""

        pictures = model.Gallery.query.get(gallery_id).pictures

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

    def arrange_gallery_display(self):
        """Arranges display for galleries, in rows by descending height."""

        total_width = sum([self.pics[p].w for p in self.pics])
        gallery_width = (total_width / 2.0) + (total_width / self.n)

        self.height_sort.reverse()

        gallery_height = self.pics[self.height_sort[0]].h
        current_row_width = 0
        current_row_top = 0

        # Hang pictures in rows
        for p in self.height_sort:
            # Start a new row if this one is full
            if (current_row_width + self.pics[p].w) > gallery_width:
                current_row_top = gallery_height
                gallery_height += self.pics[p].h
                current_row_width = 0

            self.pics[p].x1 = current_row_width
            self.pics[p].x2 = self.pics[p].x1 + self.pics[p].w
            self.pics[p].y1 = current_row_top
            self.pics[p].y2 = self.pics[p].y1 + self.pics[p].h

            current_row_width += self.pics[p].w

            # print self.pics[p].x1
            # print self.pics[p].x2
            # print self.pics[p].y1
            # print self.pics[p].y2

            # print( self.pics[p] )

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

    def arrange_column_heuristic(self):
        """Arrange in columns by a few rules."""

        self.pics_remaining = set(self.pics.keys())
        self.columns = []

        # Use the largest picture alone
        self.make_single_column()

        # For each 7 or 8 pictures make a nest, and a 2 or 3 stack
        # Written as while loop to tolertate small numbers
        i = 0
        while (i < (self.n / 7)) and (len(self.pics_remaining) > 5):
            self.make_nested_column()
            self.make_stacked_column(random.choice([2, 3]))
            i += 1

        # Then make stacks as long as possible
        while len(self.pics_remaining) > 2:
            self.make_stacked_column(random.choice([2, 3]))

        while len(self.pics_remaining) > 1:
            self.make_stacked_column(2)

        # Create single columns for the rest of the pictures while testing functionality
        while self.pics_remaining:
            self.make_single_column()

        self.combine_columns()

    def combine_columns(self):
        """Place columns together in a wall.

        Currently uses a reandom order of the generated columns.
        """

        random.shuffle(self.columns)

        wall_width = 0
        for column in self.columns:
            # print "*"*20
            # print column
            # for p in column:
            #     print(self.pics[p])
            col_width = max([self.pics[p].x2 for p in column])
            col_height_shift = max([self.pics[p].y2 for p in column]) / 2.0

            for p in column:
                self.pics[p].x1 += wall_width
                self.pics[p].x2 += wall_width
                self.pics[p].y1 += - col_height_shift
                self.pics[p].y2 += - col_height_shift

            wall_width += col_width

    def make_single_column(self):
        """Create a column with the single tallest picture remaining."""

        i = -1
        while self.height_sort[i] not in self.pics_remaining:
            i += -1
        tallest = self.height_sort[i]
        self.pics_remaining.remove(tallest)

        self.columns.append([tallest])
        self.pics[tallest].x1 = 0
        self.pics[tallest].x2 = self.pics[tallest].w
        self.pics[tallest].y1 = 0
        self.pics[tallest].y2 = self.pics[tallest].h

    def make_stacked_column(self, n):
        """Create a column with two stacked pictures."""

        stack = random.sample(self.pics_remaining, n)
        self.columns.append(stack)

        width_col = max([self.pics[p].w for p in stack])
        height_col = 0

        for p in stack:
            self.pics_remaining.remove(p)

            self.pics[p].x1 = (width_col - self.pics[p].w) / 2.0
            self.pics[p].x2 = self.pics[p].x1 + self.pics[p].w
            self.pics[p].y1 = height_col
            self.pics[p].y2 = self.pics[p].y1 + self.pics[p].h

            height_col = self.pics[p].y2

    def make_nested_column(self):
        """Create a column with wide pic and two skinny ones."""

        # Get the widest remaining picture
        i = -1
        while self.width_sort[i] not in self.pics_remaining:
            i += -1
        single = self.width_sort[i]

        # Get a pair from the skinny end of the gallery
        # TODO: add some variation in the small items slected
        pair = []
        i = 0
        while len(pair) < 2:
            if (self.width_sort[i] in self.pics_remaining):
                pair.append(self.width_sort[i])
            i += 1
        # Vary which is placed on which side of the nesting
        random.shuffle(pair)
        pair1 = pair[0]
        pair2 = pair[1]

        self.columns.append([single, pair1, pair2])

        # Remove these from the pictures to be used
        self.pics_remaining.remove(single)
        self.pics_remaining.remove(pair2)
        self.pics_remaining.remove(pair1)

        pair_width = self.pics[pair1].w + self.pics[pair2].w
        single_width = self.pics[single].w

        # Handle the horizontal placements
        col_width = max(pair_width, single_width)
        pair_margin = (col_width - pair_width) / 3.0

        self.pics[single].x1 = (col_width - single_width) / 2.0
        self.pics[single].x2 = self.pics[single].x1 + self.pics[single].w

        self.pics[pair1].x1 = pair_margin
        self.pics[pair1].x2 = pair_margin + self.pics[pair1].w

        self.pics[pair2].x1 = self.pics[pair1].x2 + pair_margin
        self.pics[pair2].x2 = self.pics[pair2].x1 + self.pics[pair2].w

        if random.random() > 0.5:
            # Place single above
            self.pics[single].y1 = 0
            self.pics[single].y2 = self.pics[single].h

            self.pics[pair1].y1 = self.pics[single].y2
            self.pics[pair1].y2 = self.pics[pair1].y1 + self.pics[pair1].h

            self.pics[pair2].y1 = self.pics[single].y2
            self.pics[pair2].y2 = self.pics[pair2].y1 + self.pics[pair2].h
        else:
            pair_height = (self.pics[pair1].h + self.pics[pair2].h)

            self.pics[single].y1 = pair_height
            self.pics[single].y2 = pair_height + self.pics[single].h

            self.pics[pair1].y1 = pair_height - self.pics[pair1].h
            self.pics[pair1].y2 = self.pics[pair1].y1 + self.pics[pair1].h

            self.pics[pair2].y1 = pair_height - self.pics[pair2].h
            self.pics[pair2].y2 = self.pics[pair2].y1 + self.pics[pair2].h

    def arrange_linear(self):
        """Arrange gallery pictures in horizontal line, vertically centered."""

        mid_index = self.n / 2
        smaller_pics = self.area_sort[:mid_index]
        larger_pics = self.area_sort[mid_index:]
        random.shuffle(smaller_pics)
        random.shuffle(larger_pics)

        row_width = 0

        for i in range(len(self.pics)):
            p = larger_pics.pop() if (i % 2 == 0) else smaller_pics.pop()
            self.pics[p].x1 = row_width
            self.pics[p].x2 = row_width + self.pics[p].w
            self.pics[p].y1 = -self.pics[p].h / 2.0
            self.pics[p].y2 = self.pics[p].h + self.pics[p].y1

            row_width = self.pics[p].x2

    def readjust_for_wall(self):
        """Readjust coordinates to + quadrant, and remove margins from pictures."""

        # These calls readjust the workspace to the origin, calculate precise
        # placments for wall hanging, and save other information for display
        self.realign_to_origin()
        self.get_wall_size()
        self.produce_placements()

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

        for p in self.pics:
            self.pics[p].remove_margin()



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

    def __repr__(self):
        """Representation format for output."""

        return "<{:s}, x1: {:.1f} x2: {:.1f} y1: {:.1f} y2: {:.1f}>".format(
            self.picture.display_name,
            self.x1,
            self.x2,
            self.y1,
            self.y2)

    def remove_margin(self):
        """Adjusts placement to that used for actual picture without margin.

        Also removes the rounding applied for arrangment.
        """

        # Durring arrangment * = (x1, y1):
        #     *--------+
        #     | +----+ |
        #     | |    | |
        #     | +----+ |
        #     +--------+
        #
        # For placement after removing margin * = (x1, y1):
        #     +        +
        #       *----+
        #       |    |
        #       +----+
        #     +        +

        width_padding = (self.w - self.picture.width) / 2.0
        height_padding = (self.h - self.picture.height) / 2.0

        self.x1 += width_padding
        self.y1 += height_padding
        # Only the upper left (x1, y1) is needed for placement, for consistincy
        # also adjust the values of x2 and y2 (Could also adjust width/height here)
        self.x2 += - width_padding
        self.y2 += - height_padding

