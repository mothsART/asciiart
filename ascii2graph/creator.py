import os
import svgwrite
from PIL import Image


class Style:
    fill = 'white'
    stroke = 'black'


class DiagramCreator:
    style = Style()
    group = None

    def __init__(self, size, dwg, diagrams):
        self.size = size
        self.dwg = dwg
        self.diagrams = diagrams

    def create(self):
        for diagram in self.diagrams:
            self._create_diagram(diagram)

            texts = diagram.text.get()

            # vertical align when addition of padding-top and padding-bottom are not pair
            vertical_align = 0
            if ((diagram.height - len(texts)) % 2 == 1):
                vertical_align = self.size / 2
            for text in texts:
                self.group.add(self.dwg.text(
                    text=texts[text][1].strip(),
                    dx=[texts[text][0] * self.size],
                    dy=[text * self.size * 2 + vertical_align],
                    textLength=len(texts[text][1].strip()) * self.size
                ))

    def _create_diagram(self, diagram):
        self.group = self.dwg.add(self.dwg.g(
            transform='translate(%s, %s)' % (
                self.size * diagram.x,
                2 * self.size * diagram.y
            )
        ))
        self.group.add(self.dwg.rect(
            (0, 0),
            (self.size * diagram.width, 2 * self.size * diagram.height),
            fill=self.style.fill, stroke=self.style.stroke)
        )


class OvaleDiagramCreator(DiagramCreator):
    pass


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
        diagramCreator = DiagramCreator(size, self.dwg, ascii_parser.diagrams)
        diagramCreator.create()

        # Ovale Diagrams
        ovaleDiagramCreator = OvaleDiagramCreator(size, self.dwg, ascii_parser.ovale_diagrams)
        ovaleDiagramCreator.create()

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
