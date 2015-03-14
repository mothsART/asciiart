from .grid import Point, Grid


class Corners:
    top_left = '+'
    top_right = '+'
    bottom_left = '+'
    bottom_right = '+'


class Rectangle:
    class_ = None
    text = None

    def __init__(self, x1, x2, y1, y2):
        self.x = x1
        self.y = y1
        self.x2 = x2
        self.y2 = y2
        self.width = x2 - x1
        self.height = y2 - y1
        self.parent = None
        self.childs = []

    def __str__(self):
        return 'value: "{0}" x: "{1}" y: "{2}" x2: "{3} y2: {4}'.format(
            hash(self), self.x, self.y, self.x2, self.y2
        )


class Line(Point):
    """ diff with Point :
        * Point = only one caracter
        * Line = multi caracteres on same vertical coordinates (y)
    """
    pass


class TextDiagram:
    def __init__(self):
        self._is_optimize = False
        self._lines = []

    def _optimization(self):
        for line in self._lines:
            if line.value.strip() == '':
                self._lines.remove(line)
        self._is_optimize = True

    def __str__(self):
        if not self._is_optimize:
            self._optimization()
        string = ''.join([str(line) + '\n' for line in self._lines])
        # suppress last Carriage return
        return string[:-1]

    def __iter__(self):
        if not self._is_optimize:
            self._optimization()
        for line in self._lines:
            yield line

    def __len__(self):
        return len(self._lines)

    def add(self, point):
        for line in self._lines:
            if point.y == line.y:
                line.value += point.value
                return
        self._lines.append(Line(
            point.value, point.x, point.y
        ))


class RectangleCreator:
    horizontal_c = ['-', '=']
    vertical_c = ['|', ':']

    def __init__(self, grid):
        self.corners = Corners()

        self.diagrams = []
        self.rectangles = []
        self.grid = grid
        for point in self.points:
            new_rectangle = self._create(point)

    @property
    def points(self):
        yield from self.grid.search('+')

    def _create(self, point):
        self.class_ = None
        x1 = point.x
        y1 = point.y
        # left to right
        i = 1
        while True:
            value = self.grid.value(x=point.x + i, y=point.y)
            if value == self.corners.top_right:
                point = Point(value, x=point.x + i, y=point.y)
                break
            if value == '=':
                self.class_ = "dashed"
            if value not in self.horizontal_c:
                return False
            i += 1
        # top to bottom
        i = 1
        while True:
            value = self.grid.value(x=point.x, y=point.y + i)
            if value == self.corners.bottom_right:
                point = Point(value, x=point.x, y=point.y + i)
                x2 = point.x
                break
            if value == ':':
                self.class_ = "dashed"
            if value not in self.vertical_c:
                return False
            i += 1
        # right to left
        i = 1
        while True:
            value = self.grid.value(x=point.x - i, y=point.y)
            if value == self.corners.bottom_left:
                point = Point(value, x=point.x - i, y=point.y)
                y2 = point.y
                break
            if value == '=':
                self.class_ = "dashed"
            if value not in self.horizontal_c:
                return False
            i += 1
        # bottom to top
        i = 1
        while True:
            value = self.grid.value(x=point.x, y=point.y - i)
            if value == self.corners.top_left:
                point = Point(value, x=point.x, y=point.y - i)
                break
            if value == ':':
                self.class_ = "dashed"
            if value not in self.vertical_c:
                return False
            i += 1

        rectangle = Rectangle(x1, x2 + 1, y1, y2)
        rectangle.class_ = self.class_
        self.rectangles.append(rectangle)
        return True


class OvaleRectangleCreator(RectangleCreator):
    def __init__(self, grid):
        self.corners = Corners()
        self.corners.top_left = '/'
        self.corners.top_right = '\\'
        self.corners.bottom_left = '\\'
        self.corners.bottom_right = '/'

        self.diagrams = []
        self.rectangles = []
        self.grid = grid
        for point in self.points:
            new_rectangle = self._create(point)

    @property
    def points(self):
        yield from self.grid.search('/')
        yield from self.grid.search('\\')


class AsciiParser:
    def __init__(self, lines):
        self.rectangles = []
        self.diagrams = []

        self.grid = Grid(lines)
        self.sorted_rectangles = []

        diagram_creator = RectangleCreator(self.grid)
        ovale_diagram_creator = OvaleRectangleCreator(self.grid)

        self.ovale_rectangles = [diagram for diagram in ovale_diagram_creator.rectangles]
        self.rectangles = [diagram for diagram in diagram_creator.rectangles]

        rectangles = self.ovale_rectangles + self.rectangles

        self.intersection(rectangles)

        for rectangle in self.sorted_rectangles:
            self.get_diagram(rectangle)

        self.diagrams = sorted(
            self.diagrams,
            key=lambda diagram: diagram.width,
            reverse=True
        )

        # for d in self.diagrams:
        #     print(d)

    def intersection(self, rectangles):
        # Sorted by width
        self.sorted_rectangles = sorted(
            rectangles,
            key=lambda rectangle: rectangle.width
        )
        for index, rectangle in enumerate(self.sorted_rectangles):
            if index + 1 == len(self.sorted_rectangles):
                break
            self._heritage(self.sorted_rectangles[index + 1::], rectangle)

    def _heritage(self, greaters_rectangles, rectangle):
        for greater_rectangle in greaters_rectangles:
            if (
                greater_rectangle.x < rectangle.x
                and greater_rectangle.x2 > rectangle.x2
            ):
                greater_rectangle.childs.append(rectangle)
                rectangle.parent = greater_rectangle
                return

    def hierarchy(self):
        """ Print Hierarchy """
        for rectangle in reversed(self.sorted_rectangles):
            print('>>>', rectangle)
            if rectangle.parent:
                print('parent >')
                print(' ' * 4, rectangle.parent)
            if len(rectangle.childs) > 0:
                print('childs >')
            for child in rectangle.childs:
                print(' ' * 4, child)

    def get_diagram(
        self, rectangle,
        pattern=['-', '=', '|', ':']
    ):
        text = TextDiagram()

        grid_points = []
        for y in range(rectangle.y + 1, rectangle.y2 - 1):
            for x in range(rectangle.x + 1, rectangle.x2 - 1):
                grid_points.append(Point(
                    self.grid.value(x, y),
                    x, y
                ))
        # Keep only points not included on Diagram's child
        grid_points_without_childs = []
        for point in grid_points:
            for child in rectangle.childs:
                if(
                    point.x >= child.x and point.x <= child.x2
                    and point.y >= child.y and point.y <= child.y2
                ):
                    point.value = " "
                    text.add(point)
                else:
                    text.add(point)

        # only leaft objects
        if rectangle.childs == []:
            grid_points = []
            for y in range(rectangle.y + 1, rectangle.y2):
                for x in range(rectangle.x + 1, rectangle.x2 - 1):
                    grid_points.append(Point(
                        self.grid.value(x, y),
                        x, y - rectangle.y + 1
                    ))
            for point in grid_points:
                text.add(point)

        if str(text).strip() == 0:
            self.diagrams.append(rectangle)
            return

        rectangle.text = text
        self.diagrams.append(rectangle)
