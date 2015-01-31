import os
import svgwrite
from PIL import Image


class SubString(str):
    start = 0
    end = 0


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
    except ValueError:
        return SubString()

    result = SubString(s[start:end])
    result.start = start
    result.end = end
    return result


class Style:
    fill = 'white'
    stroke = 'black'


class Tspan:
    value = ''
    style = ''
    def __init__(self, value, style='normal'):
        self.value = value
        self.style = style


class DiagramCreator:
    style = Style()
    group = None

    def __init__(self, size, dwg, diagrams):
        self.size = size
        self.dwg = dwg
        self.diagrams = diagrams

    def create(self, rx=0, ry=0):
        for diagram in self.diagrams:
            self._create_diagram(diagram, rx, ry)

            texts = diagram.text.get()

            # vertical align when addition of padding-top and padding-bottom are not pair
            vertical_align = 0
            if ((diagram.height - len(texts)) % 2 == 1):
                vertical_align = self.size / 2
            for text in texts:
                # horizontal align when addition of padding-left and padding-right are not pair
                # or when no space left and right
                horizontal_align = 0
                if (
                    (diagram.width - len(texts[text][1])) % 2 == 1
                    or diagram.width - 2 == len(texts[text][1])
                ):
                    horizontal_align = self.size

                # find a strong indication
                inner_text = texts[text][1].rstrip()

                tspan_list = []
                first_pattern = "**"
                last_pattern = "**"
                while True:
                    substr = find_between(inner_text, first_pattern, last_pattern)
                    if substr == '':
                        tspan = Tspan(inner_text)
                        tspan_list.append(tspan)
                        break
                    tspan = Tspan(inner_text[:substr.start - len(first_pattern)])
                    tspan_list.append(tspan)
                    tspan = Tspan(substr, 'strong')
                    tspan_list.append(tspan)
                    inner_text = inner_text[substr.end + len(last_pattern):]

                first_text = tspan_list.pop(0).value
                length = len(first_text.lstrip()) + sum([len(t.value) for t in tspan_list])
                textNode = self.group.add(self.dwg.text(
                    text=first_text,
                    dx=[horizontal_align + (len(first_text) - len(first_text.lstrip())) * self.size],
                    dy=[text * self.size * 2 + vertical_align],
                    textLength=length * self.size
                ))

                for t in tspan_list:
                    tspan_node = self.dwg.tspan(t.value)
                    if t.style == 'normal':
                        tspan_node = self.dwg.tspan(t.value)
                    else:
                        tspan_node = self.dwg.tspan(t.value, class_=t.style)
                    node = textNode.add(tspan_node)

                strong_list = []

    def _create_diagram(self, diagram, rx=0, ry=0):
        self.group = self.dwg.add(self.dwg.g(
            transform='translate(%s, %s)' % (
                self.size * diagram.x,
                2 * self.size * diagram.y
            )
        ))
        rectangle = self.dwg.rect(
            (0, 0),
            (self.size * diagram.width, 2 * self.size * diagram.height),
            fill=self.style.fill, stroke=self.style.stroke,
            rx=rx, ry=ry
        )
        self.group.add(rectangle)


class OvaleDiagramCreator(DiagramCreator):
    rx = 1
    ry = 1
    def create(self, rx=0, ry=0):
        return super().create(
            rx=self.rx * self.size,
            ry=self.ry * self.size
        )


class SVGPicture:
    def __init__(self, path=None):
        self.path = path

    def create(self, ascii_parser, size=1):
        self.dwg = svgwrite.Drawing(
            self.path, profile='full'
        )
        self.dwg.add_stylesheet('static/style.css', title='style_css')
        #self.dwg.container.Style(content='font-size: 5px;')

        # Diagrams
        diagram_creator = DiagramCreator(
            size, self.dwg, ascii_parser.diagrams
        )
        diagram_creator.create()

        # Ovale Diagrams
        ovale_diagram_creator = OvaleDiagramCreator(
            size, self.dwg, ascii_parser.ovale_diagrams
        )
        ovale_diagram_creator.create()

        # Rectangles
        for rectangle in ascii_parser.rectangles:
            self.dwg.add(self.dwg.rect(
                (size * rectangle.x, size * rectangle.y),
                (size * rectangle.width, size * rectangle.height),
                fill='white', stroke='black')
            )
        self.dwg.save()


class BitmapPicture:
    def __init__(self, path=None, zoom=1):
        pass

    def create(self, ascii_parser):
        pass


class PictureCreator:
    def __init__(self, output_file=None):
        path, extension = os.path.splitext(output_file)
        if extension == '.svg':
            self.output_picture = SVGPicture(output_file)
        else:
            self.output_picture = BitmapPicture(output_file)

    def create(self, ascii_parser=None, size=1):
        self.output_picture.create(ascii_parser, size)
        # try:
        #     Image.open(infile).save(outfile)
        # except IOError:
        #     print("cannot convert", infile)
