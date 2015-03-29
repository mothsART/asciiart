#import pudb
import copy
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
        * Point = only one character
        * Line = multi characters on same vertical coordinates (y)
    """
    pass


class TextDiagram:
    def __init__(self):
        self._is_optimize = False
        self._lines = []

    def _split_lines(self, line):
        sub_str = line.value.split(" ")

        line_list = []

        x = 0
        value = ""
        len_lspace = len(value) - len(value.lstrip())
        for i, item in enumerate(sub_str):
            if item == "":
                x += 1
                continue
            try:
                if sub_str[i + 1] == "":
                    value = value + item
                    line_list.append(Line(value, x + len_lspace, line.y))
                    value = ""
                    x = 0
                else:
                    value = value + item + " "
            except IndexError:
                value = value + item
                line_list.append(Line(value, x + len_lspace, line.y))
        return line_list

    def _optimization(self):
        empty_lines = []
        for line in self._lines:
            len_lspace = len(line.value) - len(line.value.lstrip())
            line.x = len_lspace
            line.value = line.value.strip()

            if line.value == '':
                empty_lines.append(line)
        # Remove duplicates and sorted by vertical coordinates
        self._lines = sorted(
            list(set(self._lines) - set(empty_lines)),
            key=lambda line: line.y
        )

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

        #pudb.set_trace()
        self.diagrams = sorted(
            self.diagrams,
            key=lambda diagram: diagram.width,
            reverse=True
        )

        # for d in self.diagrams:
        #     print(d)

        # self.hierarchy()

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
                and greater_rectangle.y < rectangle.y
                and greater_rectangle.y2 > rectangle.y2
            ):
                greater_rectangle.childs.append(rectangle)
                rectangle.parent = greater_rectangle
                return

    def _travel_hierarchy(self, rectangle, inc=0, prefix='├'):
        print(" " * (4 * inc), sep="", end="")
        print(prefix + '──►', rectangle)
        if rectangle.childs != []:
            for child_inc, child in enumerate(rectangle.childs):
                child_prefix = '├'
                if child_inc == len(rectangle.childs) - 1:
                    child_prefix = '└'
                self._travel_hierarchy(child, inc + 1, prefix=child_prefix)

    def hierarchy(self):
        """ Print Hierarchy """
        rectangle_without_hierarchy = []
        for rectangle in reversed(self.sorted_rectangles):
            if not rectangle.parent and rectangle.childs == []:
                rectangle_without_hierarchy.append(rectangle)

        # display
        if rectangle_without_hierarchy != []:
            print('┌────────────────────────────────┐')
            print('│ rectangle(s) without hierarchy │')
            print('├────────────────────────────────┘')
            prefix = '├'
            for inc, rectangle in enumerate(rectangle_without_hierarchy):
                if (inc == len(rectangle_without_hierarchy) - 1):
                    prefix = '└'
                print(prefix + '──►', rectangle)

        sorted_rectangles = list(
            set(self.sorted_rectangles)
            - set(rectangle_without_hierarchy)
        )
        parents_rectangles = []
        for rectangle in reversed(sorted_rectangles):
            if not rectangle.parent:
                parents_rectangles.append(rectangle)

        print('┌─────────────────────────────┐')
        print('│ rectangle(s) with hierarchy │')
        print('└─────────────────────────────┘')
        for rectangle in parents_rectangles:
            self._travel_hierarchy(rectangle, prefix='─')

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
            new_point = copy.copy(point)
            new_point.y = point.y - rectangle.y + 1
            for child in rectangle.childs:
                if(
                    point.x >= child.x and point.x <= child.x2
                    and point.y >= child.y and point.y <= child.y2
                ):
                    new_point.value = " "
                    text.add(new_point)
                else:
                    #if point.value != " ":
                        #print(rectangle.y, "<===>", new_point.y, "<==>", point.y)
                    text.add(new_point)
        #print('=================')

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
