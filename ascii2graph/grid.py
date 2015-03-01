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
