import math
import random
from functools import wraps

# Note: unable to import Gallery from model specifically because model imports arrange too
import model

DEFAULT_MARGIN = 2

# Decorator for instance methods of workspace
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def adjust_for_wall(func):

    # This decorator does not have access to instance
    @wraps(func)
    def wrapper(self):

        # This wrapper does have access to instance

        # Calling the arrangement function
        func(self)

        # These calls readjust the workspace to the origin, calculate precise
        # placments for wall hanging, and save other information for display
        self.realign_to_origin()
        self.get_wall_size()
        self.remove_margins()

    return wrapper

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Arranger(object):
    """Arranges items in a workspace. Base class"""

    def __init__(self, workspace):

        self.ws = workspace

        # TODO: Arrangment tracking that is calc'ed once from workspace stuff
        self.pics_remaining = set(self.ws.pics.keys())

        # TODO: reimplement
        # Because it is common to need the largest, tallest, smallest, etc,
        # prepare these ahead fo time for the workspace
        self.area_sort = sorted([self.ws.pics[p].id for p in self.ws.pics],
                                key=lambda x: self.ws.pics[x].a)
        self.width_sort = sorted([self.ws.pics[p].id for p in self.ws.pics],
                                 key=lambda x: self.ws.pics[x].w)
        self.height_sort = sorted([self.ws.pics[p].id for p in self.ws.pics],
                                  key=lambda x: self.ws.pics[x].h)

    # Methods to select rough sizes/heights/widths or other elections for use in
    # arrangments

    def pop_any_n(self, n):
        """ Return any n remaining pictures, removes returned from pictures remaining."""

        ps = random.sample(self.pics_remaining, n)
        for p in ps:
            self.pics_remaining.remove(p)
        return ps

    def pop_tallest(self):
        """Return tallest picture reminaing, and remove from list of those remaining."""

        for p in self.height_sort[::-1]:
            if p in self.pics_remaining:
                self.pics_remaining.remove(p)
                return p

    def pop_widest(self):
        """Return widest picture reminaing, and remove from list of those remaining."""

        for p in self.width_sort[::-1]:
            if p in self.pics_remaining:
                self.pics_remaining.remove(p)
                return p

    def pop_narrow(self):
        """Return a picture from the narrow third of original gallery, or narrowest remaining.

        Removes returned from pictures remaining.
        """

        narrows = set(self.width_sort[:(self.ws.len / 3)]).intersection(self.pics_remaining)
        if narrows:
            p = random.sample(narrows, 1)[0]
            self.pics_remaining.remove(p)
            return p
        else:
            for p in self.width_sort:
                if p in self.pics_remaining:
                    self.pics_remaining.remove(p)
                    return p

    def pop_small(self):
        """Return a picture from the small third of areas in original gallery,
        or smallest area remaining.

        Removes returned from pictures remaining.
        """

        smalls = set(self.area_sort[:(self.ws.len / 3)]).intersection(self.pics_remaining)
        if smalls:
            p = random.sample(smalls, 1)[0]
            self.pics_remaining.remove(p)
            return p
        else:
            for p in self.area_sort:
                if p in self.pics_remaining:
                    self.pics_remaining.remove(p)
                    return p

    def pop_large(self):
        """Return a picture from the large third of areas in original gallery,
        or largest area remaining.

        Removes returned from pictures remaining.
        """

        larges = set(self.area_sort[-(self.ws.len / 3):]).intersection(self.pics_remaining)
        if larges:
            p = random.sample(larges, 1)[0]
            self.pics_remaining.remove(p)
            return p
        else:
            for p in self.area_sort[::-1]:
                if p in self.pics_remaining:
                    self.pics_remaining.remove(p)
                    return p

    @property
    def height_tallest(self):
        """Height of the tallest picture."""

        return self.height_sort[-1]


    # Methods used for each arrangement (so far)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def realign_to_origin(self):
        """Shift all placements to positive quadrant with origin upper left."""

        x1s = [self.ws.pics[p].x1 for p in self.ws.pics]
        y1s = [self.ws.pics[p].y1 for p in self.ws.pics]

        x_shift = -min(x1s)
        y_shift = -min(y1s)

        for pic in self.ws.pics:
            self.ws.pics[pic].x1 += x_shift
            self.ws.pics[pic].x2 += x_shift
            self.ws.pics[pic].y1 += y_shift
            self.ws.pics[pic].y2 += y_shift

    def get_wall_size(self):
        """Assgins as attributes the total wall height and width."""

        x1s = [self.ws.pics[p].x1 for p in self.ws.pics]
        x2s = [self.ws.pics[p].x2 for p in self.ws.pics]
        y1s = [self.ws.pics[p].y1 for p in self.ws.pics]
        y2s = [self.ws.pics[p].y2 for p in self.ws.pics]

        # If already adjusted to origin the second term of each expression is unnecesary
        self.ws.width = max(x2s) - min(x1s)
        self.ws.height = max(y2s) - min(y1s)

    def remove_margins(self):
        """Convert coordinates: remove rounding and margins used for placement."""

        for p in self.ws.pics:
            self.ws.pics[p].remove_margin()

    # Methods used in potentially mutiple arrangement types
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def pull_in_picture(self, pic_id):
        """From placed workspace, step single picture towards center if possible.

        Return boolean true if pictures is moved.
        """

        move = False

        pic = self.ws.pics[pic_id]

        x_inc = -1 if ((pic.x1+pic.x2)/float(2)) > 0 else 1
        y_inc = -1 if ((pic.y1+pic.y2)/float(2)) > 0 else 1

        # this inhenrently does one move before other, scramble?
        if not self.any_conflict(pic.x1+x_inc, pic.x2+x_inc, pic.y1, pic.y2, pic):
            pic.x1 += x_inc
            pic.x2 += x_inc
            move = True
        if not self.any_conflict(pic.x1, pic.x2, pic.y1+y_inc, pic.y2+y_inc, pic):
            pic.y1 += y_inc
            pic.y2 += y_inc
            move = True

        return move

    def any_conflict(self, x1_try, x2_try, y1_try, y2_try, this_pic=None):
        """Check placed pictures, return true if any conflict with this placement."""

        # Check each picture in workspace
        for p in self.ws.pics:
            pic = self.ws.pics[p]
            if (pic.x1 is not None) and (pic is not this_pic):
                # This picture has been placed, so check for conflict
                if is_conflict(pic.x1, pic.x2, pic.y1, pic.y2,
                               x1_try, x2_try, y1_try, y2_try):
                    # Conflicts with attempted placement, fail fast

                    return True

        # No conflicts found
        return False


class GalleryFloorArranger(Arranger):
    """Arranges display for galleries, in rows by descending height, aligned bottom."""

    @adjust_for_wall
    def arrange(self):
        """Arranges display for galleries, in rows by descending height, aligned bottom."""

        # Make two rows if many pictures, one row if not
        total_width = sum([self.ws.pics[p].w for p in self.ws.pics])
        if self.ws.len < 10:
            gallery_width = (total_width) + (total_width / self.ws.len)
        else:
            gallery_width = (total_width / 2.0) + (total_width / self.ws.len)

        gallery_height = self.height_tallest
        current_row_width = 0
        current_row_base = gallery_height

        # Set pictures in rows
        while self.pics_remaining:

            p = self.pop_tallest()

            # Start a new row if this one is full
            if (current_row_width + self.ws.pics[p].w) > gallery_width:
                gallery_height += self.ws.pics[p].h
                current_row_width = 0 # random.choice([-4,4])
                current_row_base = gallery_height

            self.ws.pics[p].x1 = current_row_width
            self.ws.pics[p].x2 = self.ws.pics[p].x1 + self.ws.pics[p].w
            self.ws.pics[p].y2 = current_row_base
            self.ws.pics[p].y1 = self.ws.pics[p].y2 - self.ws.pics[p].h

            current_row_width += self.ws.pics[p].w


class ColumnArranger(Arranger):
    """Arrange in columns by a few rules."""

    @adjust_for_wall
    def arrange(self):
        """Arrange in columns by a few rules."""

        self.columns = []

        # Use the largest picture alone
        self.make_single_column()

        # For each 7 or 8 pictures make a nest, and a 2 or 3 stack
        # Written as while loop to tolertate small numbers
        i = 0
        while (i < (self.ws.len / 7)) and (len(self.pics_remaining) > 5):
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

        Currently uses a random order of the generated columns.
        """

        random.shuffle(self.columns)

        wall_width = 0
        for column in self.columns:
            col_width = max([self.ws.pics[p].x2 for p in column])
            col_height_shift = max([self.ws.pics[p].y2 for p in column]) / 2.0

            for p in column:
                self.ws.pics[p].x1 += wall_width
                self.ws.pics[p].x2 += wall_width
                self.ws.pics[p].y1 += - col_height_shift
                self.ws.pics[p].y2 += - col_height_shift

            wall_width += col_width

    def make_single_column(self):
        """Create a column with the single tallest picture remaining."""

        tallest = self.pop_tallest()

        self.columns.append([tallest])
        self.ws.pics[tallest].x1 = 0
        self.ws.pics[tallest].x2 = self.ws.pics[tallest].w
        self.ws.pics[tallest].y1 = 0
        self.ws.pics[tallest].y2 = self.ws.pics[tallest].h

    def make_stacked_column(self, n):
        """Create a column with two stacked pictures."""

        stack = self.pop_any_n(n)
        self.columns.append(stack)

        width_col = max([self.ws.pics[p].w for p in stack])
        height_col = 0

        for p in stack:
            self.ws.pics[p].x1 = (width_col - self.ws.pics[p].w) / 2.0
            self.ws.pics[p].x2 = self.ws.pics[p].x1 + self.ws.pics[p].w
            self.ws.pics[p].y1 = height_col
            self.ws.pics[p].y2 = self.ws.pics[p].y1 + self.ws.pics[p].h

            height_col = self.ws.pics[p].y2

    def make_nested_column(self):
        """Create a column with wide pic and two skinny ones."""

        # Get the widest remaining picture
        single = self.pop_widest()

        # Get a pair from the skinny end of the gallery
        pair1 = self.pop_narrow()
        pair2 = self.pop_narrow()

        self.columns.append([single, pair1, pair2])

        pair_width = self.ws.pics[pair1].w + self.ws.pics[pair2].w
        single_width = self.ws.pics[single].w

        # Handle the horizontal placements
        col_width = max(pair_width, single_width)
        pair_margin = (col_width - pair_width) / 3.0

        self.ws.pics[single].x1 = (col_width - single_width) / 2.0
        self.ws.pics[single].x2 = self.ws.pics[single].x1 + self.ws.pics[single].w

        self.ws.pics[pair1].x1 = pair_margin
        self.ws.pics[pair1].x2 = pair_margin + self.ws.pics[pair1].w

        self.ws.pics[pair2].x1 = self.ws.pics[pair1].x2 + pair_margin
        self.ws.pics[pair2].x2 = self.ws.pics[pair2].x1 + self.ws.pics[pair2].w

        if random.random() > 0.5:
            # Place single above
            self.ws.pics[single].y1 = 0
            self.ws.pics[single].y2 = self.ws.pics[single].h

            self.ws.pics[pair1].y1 = self.ws.pics[single].y2
            self.ws.pics[pair1].y2 = self.ws.pics[pair1].y1 + self.ws.pics[pair1].h

            self.ws.pics[pair2].y1 = self.ws.pics[single].y2
            self.ws.pics[pair2].y2 = self.ws.pics[pair2].y1 + self.ws.pics[pair2].h
        else:
            pair_height = (self.ws.pics[pair1].h + self.ws.pics[pair2].h)

            self.ws.pics[single].y1 = pair_height
            self.ws.pics[single].y2 = pair_height + self.ws.pics[single].h

            self.ws.pics[pair1].y1 = pair_height - self.ws.pics[pair1].h
            self.ws.pics[pair1].y2 = self.ws.pics[pair1].y1 + self.ws.pics[pair1].h

            self.ws.pics[pair2].y1 = pair_height - self.ws.pics[pair2].h
            self.ws.pics[pair2].y2 = self.ws.pics[pair2].y1 + self.ws.pics[pair2].h


class LinearArranger(Arranger):
    """Arrange gallery pictures in horizontal line, vertically centered."""

    @adjust_for_wall
    def arrange(self):

        row_width = 0

        for i in range(len(self.ws.pics)):
            p = self.pop_large() if (i % 2 == 0) else self.pop_any_n(1)[0]
            self.ws.pics[p].x1 = row_width
            self.ws.pics[p].x2 = row_width + self.ws.pics[p].w
            self.ws.pics[p].y1 = -self.ws.pics[p].h / 2.0
            self.ws.pics[p].y2 = self.ws.pics[p].h + self.ws.pics[p].y1

            row_width = self.ws.pics[p].x2


class GridArranger(Arranger):

    @adjust_for_wall
    def arrange(self):
        """Arrangment via an initial placement in a grid."""

        # pics_in_grid = self.random_place_in_grid()
        pics_in_grid = self.large_center_place_in_grid()

        self.expand_grid_to_arrangment(pics_in_grid)

        self.pull_in_pictures()

    def random_place_in_grid(self):
        """Place pics in random grid indicies.

        Returns a dict of tuple keys of grid indicies with pic id values
        {(i,j): pic}
        """

        n_grid = int(math.ceil(math.sqrt(self.ws.len)))
        min_grid = -n_grid/2
        max_grid = min_grid + n_grid

        grid_pairs = [(i, j) for i in range(min_grid, max_grid)
                             for j in range(min_grid, max_grid)]

        grid_sample = random.sample(grid_pairs, self.ws.len)

        grid_pics = {grid_sample[i]:pic for i, pic in enumerate(self.ws.pics.keys())}
        print grid_pics
        return grid_pics

    def large_center_place_in_grid(self):
        """Place pics in random grid indicies but with larger ones roughly towards center.

        Returns a dict of tuple keys of grid indicies with pic id values
        {(i,j): pic}
        """

        n_grid = int(math.ceil(math.sqrt(self.ws.len))) / 2

        grid_pairs = [(i, j) for i in range(-n_grid, n_grid+1)
                             for j in range(-n_grid, n_grid+1)]
        print grid_pairs
        grid_sample = set(random.sample(grid_pairs, self.ws.len))
        print grid_sample
        cols, rows = zip(*grid_sample)
        mag_sort_j = sorted(set(cols), key=abs)
        mag_sort_i = sorted(set(rows), key=abs)

        print mag_sort_j
        print mag_sort_i

        grid_pics = {}

        for i in mag_sort_i:
            for j in mag_sort_j:
                if (i, j) in grid_sample:
                    grid_pics[(i, j)] = self.pop_large()
                    # print( grid_pics[(i, j)] )
                    print self.ws.pics[grid_pics[(i, j)]], ' at ',(i, j) 
                if not self.pics_remaining:
                    return grid_pics

    def expand_grid_to_arrangment(self, pics_in_grid):
        """From a set of grid indicies produce geometrically valid placements.

        (grid = relative psuedo locations without geometry)"""

        cols, rows = zip(*pics_in_grid.keys())
        mag_sort_j = sorted(set(cols), key=abs)
        mag_sort_i = sorted(set(rows), key=abs)

        # Ugh. HTML canvas coordinates:
        #        ^
        #  -i,-j | i,-j
        # <------+------>
        #  -i,j  | i,j
        #        v

        for i in mag_sort_i:
            for j in mag_sort_j:

                pic_id = pics_in_grid.get((i, j), None)

                if pic_id:
                    # Picture existed at that grid location, place in workspace
                    self.walk_out_to_place(pic_id, (i, j))


    def pull_in_pictures(self):
        """From placed workspace, where possible bring pictures towards center.

        Although this code might work on a non-centered arrangmet I suspec the
        results would be gnarly.
        """
        moves = 1
        count = 0

        while moves > 0 and count < 500:

            moves = 0
            count += 1

            scrambled_pics = self.ws.pics.keys()
            random.shuffle(scrambled_pics)

            # Loop through pictures
            for p in scrambled_pics:

                move = self.pull_in_picture(p)

                if move:
                    moves += 1

    def walk_out_to_place(self, pic_id, grid):
        """Given a picture and grid location, return valid workspace of placements.

        Method is a walk out diagonally in the roucgh direction of initial grid
        placement.
        """
        pic = self.ws.pics[pic_id]
        i, j = grid

        # print 'placing pic '
        # print pic.picture.display_name

        pic.x1 = j
        pic.x2 = j + pic.w
        pic.y1 = i
        pic.y2 = i + pic.h

        # Parameters for moving this placement until no conflict
        # Probability of movement in x or y direction at each attempt
        ratio_i = (abs(i) / float(abs(i)+abs(j))) if (abs(i)+abs(j)) > 0 else 0.5
        # increments chosen so that position is moved away from origin in given quadrant
        x_inc = 1 if j > 0 else -1
        y_inc = 1 if i > 0 else -1

        while self.any_conflict(pic.x1, pic.x2, pic.y1, pic.y2, pic):

            if random.random() < ratio_i:
                # Move in y direction
                pic.y1 += y_inc
                pic.y2 += y_inc

            else:
                # Move in x direction
                pic.x1 += x_inc
                pic.x2 += x_inc


class Workspace(object):
    """Class on which arrangments can be performed."""

    def __init__(self, gallery_id):
        """Constructor from picture list."""

        pictures = model.Gallery.query.get(gallery_id).pictures

        options = {}

        self.gallery_id = gallery_id
        self.margin = options.get('margin', DEFAULT_MARGIN)
        self.len = len(pictures)

        # self.options = options

        self.pics = {}

        for picture in pictures:

            self.pics[picture.picture_id] = Pic(picture=picture,
                                                margin=self.margin)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

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

        return "<{}, x1: {} x2: {} y1: {} y2: {}>".format(
            self.picture.display_name,
            '{:.1f}'.format(self.x1) if isinstance(self.x1, float) else str(self.x1),
            '{:.1f}'.format(self.x2) if isinstance(self.x2, float) else str(self.x2),
            '{:.1f}'.format(self.y1) if isinstance(self.y1, float) else str(self.y1),
            '{:.1f}'.format(self.y2) if isinstance(self.y2, float) else str(self.y2))

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


def is_conflict(x1_a, x2_a, y1_a, y2_a, x1_b, x2_b, y1_b, y2_b):
    """Check if the rectangles a and b described by the input coordinates overlap.

        >>> is_conflict(1, 2, 1, 2, 1, 2, 1, 2)
        True

        >>> is_conflict(1, 2, 1, 2, -2, -1, -2, -1)
        False

        >>> is_conflict(1, 10, 1, 10, 2, 4, 2, 4)
        True

        >>> is_conflict(2, 4, 2, 4, 1, 10, 1, 10,)
        True

        >>> is_conflict(1, 10, 1, 10, 2, 4, 6, 11)
        True

        >>> is_conflict(2, 4, 6, 11, 1, 10, 1, 10)
        True

        >>> is_conflict(0, 11, -1, 8, -1, 9, 0, 12)
        True

           +----+
        +----------+
        |  |    |  |
        |  |    |  |
        +----------+
           +----+

        >>> is_conflict(0, 8, 2, 6, 2, 6, 1, 7)
        True
        >>> is_conflict(2, 6, 1, 7, 0, 8, 2, 6)
        True
    """

    if (((x1_a <= x1_b <= x2_a) or (x1_a <= x2_b <= x2_a)) and
         ((y1_a <= y1_b <= y2_a) or (y1_a <= y2_b <= y2_a))):

        # This should be the case when any corner of b is within a:
        #    a               a                a
        # +------+       +--------+       +-------+
        # |      |       |        |       |       |
        # |   +-----+    |    +------+    |  +--+ |
        # |   |b |  |    |    |b  |  |    |  |b | |
        # +------+  |    |    +------+    |  +--+ |
        #     |     |    |        |       |       |
        #     +-----+    +--------+       +-------+
        # (not all possible cases shown)
        return True

    elif (((x1_b <= x1_a <= x2_b) or (x1_b <= x2_a <= x2_b)) and
         ((y1_b <= y1_a <= y2_b) or (y1_b <= y2_a <= y2_b))):

        # This should be the case when any corner of b is within a:
        #    b               b                b
        # +------+       +--------+       +-------+
        # |      |       |        |       |       |
        # |   +-----+    |    +------+    |  +--+ |
        # |   |a |  |    |    |a  |  |    |  |a | |
        # +------+  |    |    +------+    |  +--+ |
        #     |     |    |        |       |       |
        #     +-----+    +--------+       +-------+
        # (not all possible cases shown, the first case shown would be in first
        # condition too)
        return True

    elif ((x1_a < x1_b) and (x2_b < x2_a)) and ((y1_b < y1_a) and (y2_a < y2_b)):
        #      b
        #    +----+
        # +----------+
        # |a |    |  |
        # |  |    |  |
        # +----------+
        #    +----+
        return True

    elif ((x1_b < x1_a) and (x2_a < x2_b)) and ((y1_a < y1_b) and (y2_b < y2_a)):
        #      a
        #    +----+
        # +----------+
        # |b |    |  |
        # |  |    |  |
        # +----------+
        #    +----+
        return True

    else:
        return False

