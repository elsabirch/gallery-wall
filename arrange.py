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

    def arrange_grid(self):
        """Arrangment via an initial placement in a grid."""

        pics_in_grid = self.random_place_in_grid()

        self.expand_grid_to_arrangment(pics_in_grid)

        self.pull_in_placements()

    def expand_grid_to_arrangment(self, pics_in_grid):
        """From a set of grid indicies produce geometrically valid placements.

        (grid = relative psuedo locations without geometry)"""
        # print '*'*80
        cols, rows = zip(*pics_in_grid.keys())
        mag_sort_j = sorted(set(cols), key=abs)
        mag_sort_i = sorted(set(rows), key=abs)

        # Ugh. HTML canvas coordinates:
        #        ^
        #  -i,-j | i,-j
        # <------+------>
        #  -i,j  | i,j
        #        v

        print(pics_in_grid)
        print(mag_sort_i)
        print(mag_sort_j)

        for i in mag_sort_i:
            for j in mag_sort_j:

                print '*'*30
                print 'grid place: {}, {}'.format(i,j) 

                pic_id = pics_in_grid.get((i, j), None)

                if pic_id:
                    # Picture existed at that grid location, place in workspace
                    x1, x2, y1, y2 = self.walk_out_to_place(pic_id, (i, j))

                    print 'placed!'
                    self.pics[pic_id].x1 = x1
                    self.pics[pic_id].x2 = x2
                    self.pics[pic_id].y1 = y1
                    self.pics[pic_id].y2 = y2

                    print self.pics[pic_id]

    def walk_out_to_place(self, pic_id, grid):
        """Given a picture and grid placement, return valid workspace placement.

        Method is a walk out diagonally in the roucgh direction of initial grid
        placement.
        """
        pic = self.pics[pic_id]
        i, j = grid

        print 'placing pic '
        print pic.picture.display_name

        x1_try = j
        x2_try = j + pic.w
        y1_try = i
        y2_try = i + pic.h

        print 'initial place: {} {} {} {}'.format(x1_try, x2_try, y1_try, y2_try)

        # Parameters for moving this placement until no conflict
        # Probability of movement in x or y direction at each attempt
        ratio_i = (abs(i) / float(abs(i)+abs(j))) if (abs(i)+abs(j)) > 0 else 0.5
        # increments chosen so that position is moved away from origin in given quadrant
        x_inc = 1 if j > 0 else -1
        y_inc = 1 if i > 0 else -1

        while self.any_conflict(x1_try, x2_try, y1_try, y2_try):

            if random.random() < ratio_i:
                # Move in y direction
                y1_try += y_inc
                y2_try += y_inc
                print 'move to: {} {} {} {}'.format(x1_try, x2_try, y1_try, y2_try)

            else:
                # Move in x direction
                x1_try += x_inc
                x2_try += x_inc

                print 'move to: {} {} {} {}'.format(x1_try, x2_try, y1_try, y2_try)

        return (x1_try, x2_try, y1_try, y2_try)

    def pull_in_placements(self):
        """From placed workspace, where possible bring pictures towards center.

        Although this code might work on a non-centered arrangmet I suspec the
        results would be gnarly.
        """
        moves = 1
        count = 0

        while moves > 0 and count < 100:

            moves = 0
            count += 1

            # Loop through pictures
            for p in self.pics:
                pic = self.pics[p]

                x_inc = -1 if ((pic.x1+pic.x2)/float(2)) > 0 else 1
                y_inc = -1 if ((pic.y1+pic.y2)/float(2)) > 0 else 1

                # CONFLICT WILL BE FOUND WITH SELF, REWRITE CONFLICT CHECK TO 
                # EXEMPT THE PICTURE CURRENTLY IN QUESTION FROM PLACMENT CONFLICT 
                # CHECKS THAT WILL ALSO PERMIT THE USE OF X1 ETC FOR TRACKIGN 
                # DURREING PLACEMNT RATHER THAN _TRYS

                # this inhenrently does one move before other, scramble?
                if not self.any_conflict(pic.x1+x_inc, pic.x2+x_inc, pic.y1, pic.y2, pic):
                    pic.x1 += x_inc
                    pic.x2 += x_inc
                    moves += 1
                if not self.any_conflict(pic.x1, pic.x2, pic.y1+y_inc, pic.y2+y_inc, pic):
                    pic.y1 += y_inc
                    pic.y2 += y_inc
                    moves += 1

                print 'count: {} moves: {}'.format(count, moves)

    def any_conflict(self, x1_try, x2_try, y1_try, y2_try, this_pic = None):
        """Check placed pictures, return true if any conflict with this placement."""

        print 'conflict checking- - - -- - - - - - --'

        for p in self.pics:
            print '*** conflict check'

            print self.pics[p].picture.display_name
            print self.pics[p].x1
            print self.pics[p].x2
            print self.pics[p].y1
            print self.pics[p].y2
            print self.pics[p].h
            print self.pics[p].w

        # Check each picture in workspace
        for p in self.pics:
            pic = self.pics[p]
            if (pic.x1 is not None) and (pic is not this_pic):
                # This picture has been placed, so check for conflict
                if is_conflict(pic.x1, pic.x2, pic.y1, pic.y2,
                               x1_try, x2_try, y1_try, y2_try):
                    # Conflicts with attempted placement, fail fast
                    print 'conflict found with {}'.format(pic)
                    return True

        # No conflicts found
        return False

    def random_place_in_grid(self):
        """Place pics in random grid indicies.

        Returns a dict of tuple keys of grid indicies with pic id values
        {(i,j): pic}
        """

        n_grid = int(math.ceil(math.sqrt(self.n)))
        min_grid = -n_grid/2
        max_grid = min_grid + n_grid

        grid_pairs = [(i, j) for i in range(min_grid, max_grid) 
                             for j in range(min_grid, max_grid)]

        grid_sample = random.sample(grid_pairs, self.n)

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

        Currently uses a random order of the generated columns.
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
        self.pics_remaining.remove(single)

        # Get a pair from the skinny end of the gallery
        small_set = (set(self.width_sort[:(self.n / 3)]) &
                     self.pics_remaining)
        if len(small_set) < 2:
            # Old method will work for small number remaining
            pair = []
            i = 0
            while len(pair) < 2:
                if (self.width_sort[i] in self.pics_remaining):
                    pair.append(self.width_sort[i])
                i += 1
            random.shuffle(pair)
        else:
            # New method adds more vairety
            pair = random.sample(small_set, 2)

        # Vary which is placed on which side of the nesting
        pair1 = pair[0]
        pair2 = pair[1]

        self.columns.append([single, pair1, pair2])

        # Remove these from the pictures to be used
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


    """

    if ((((x1_a <= x1_b <= x2_a) or (x1_a <= x2_b <= x2_a)) and
         ((y1_a <= y1_b <= y2_a) or (y1_a <= y2_b <= y2_a)))
        or
        (((x1_b <= x1_a <= x2_b) or (x1_b <= x2_a <= x2_b)) and
         ((y1_b <= y1_a <= y2_b) or (y1_b <= y2_a <= y2_b)))):
        return True
    else:
        return False

