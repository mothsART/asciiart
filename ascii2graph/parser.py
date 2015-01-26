class Corners:
    top_left = '+'
    top_right = '+'
    bottom_left = '+'
    bottom_right = '+'


class Rectangle:
    def __init__(self, x1, x2, y1, y2):
        self.x = x1
        self.y = y1
        self.x2 = x2
        self.y2 = y2
        self.width = x2 - x1
        self.height = y2 - y1


class TextDiagram:
    left_space = True

    def __init__(self):
        self._text = {}

    def get(self, x=None, y=None):
        if y in self._text:
            return self._text[y]
        if self._text == {}:
            return False
        return self._text

    def add(self, x=0, y=0, value=''):
        if y in self._text:
            # left position
            if (value == " " and self.left_space):
                self._text[y][0] = x
            else:
                self.left_space = False
                self._text[y][1] += value
        else:
            self.left_space = True
            self._text[y] = [x, value]
        return True


class Diagram(Rectangle):
    text = None


class OvaleDiagram(Diagram):
    text = None


class DiagramCreator:
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
        x1 = point.x
        y1 = point.y
        # left to right
        i = 1
        while True:
            value = self.grid.value(x=point.x + i, y=point.y)
            if value == self.corners.top_right:
                point = Point(value, x=point.x + i, y=point.y)
                break
            if value != '-':
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
            if value != '|':
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
            if value != '-':
                return False
            i += 1
        # bottom to top
        i = 1
        while True:
            value = self.grid.value(x=point.x, y=point.y - i)
            if value == self.corners.top_left:
                point = Point(value, x=point.x, y=point.y - i)
                break
            if value != '|':
                return False
            i += 1

        diagram = self._get_diagram(x1 - 1, x2, y1, y2)
        if not diagram:
            self.rectangles.append(Rectangle(x1 - 1, x2, y1, y2))
            return True
        self.diagrams.append(diagram)
        return True

    def _get_diagram(
        self, init_x=0, end_x=0, init_y=0, end_y=0,
        pattern=['-', '|']
    ):
        text = TextDiagram()
        for y in range(init_y + 1, end_y):
            for x in range(init_x + 1, end_x):
                value = self.grid.value(x, y)
                if value not in pattern:
                    text.add(x=x - init_x, y=y - init_y, value=value)
        if not text.get():
            return False
        diagram = OvaleDiagram(init_x, end_x, init_y, end_y)
        diagram.text = text
        return diagram


class OvaleDiagramCreator(DiagramCreator):
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


class Point:
    def __init__(self, value='', x=0, y=0):
        self.value = value
        self.x = x
        self.y = y

    def __str__(self):
        return 'value: "{0}" x: "{1}" y: "{2}"'.format(
            self.value, self.x, self.y
        )


class Grid:
    max_x = 0
    max_y = 0

    def __init__(self, lines):
        self._array = {}

        for line_nb, line in enumerate(lines):
            line = line.rstrip()
            self._array[line_nb] = {}
            char_len = len(line.rstrip()) + 1
            if char_len > self.max_x:
                self.max_x = char_len
            for char_nb, character in enumerate(line):
                self._array[line_nb][char_nb] = character

        self.max_y = len(lines)

        for y in range(0, self.max_y):
            if y not in self._array:
                self._array[y] = {}
            if len(self._array[y]) < self.max_x:
                for pos in range(len(self._array[y]), self.max_x + 1):
                    self._array[y][pos] = ' '

    def __str__(self):
        stream = ''
        for y in range(0, self.max_y):
            for x in range(0, self.max_x):
                stream += self._array[y][x]
            if y != self.max_y:
                stream += '\n'
        return stream

    def value(self, x=0, y=0):
        if x > self.max_x:
            return False
        if y >= self.max_y:
            return False
        return self._array[y][x]

    def search(self, value):
        for y in range(0, self.max_y):
            for x in range(0, self.max_x):
                if self._array[y][x] == value:
                    yield Point(value, x, y)


class AsciiParser:
    def __init__(self, lines):
        self.rectangles = []
        grid = Grid(lines)
        #print(grid)
        #print(grid._array)

        diagram_creator = DiagramCreator(grid)
        ovale_diagram_creator = OvaleDiagramCreator(grid)

        self.ovale_diagrams = (diagram for diagram in ovale_diagram_creator.diagrams)
        self.diagrams = (diagram for diagram in diagram_creator.diagrams)
        self.rectangles = (rectangle for rectangle in diagram_creator.rectangles)
