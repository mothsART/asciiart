import os
import svgwrite
from PIL import Image


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
        for diagram in ascii_parser.diagrams:
            group = self.dwg.add(self.dwg.g(
                transform='translate(%s, %s)' % (
                    size * diagram.x,
                    2 * size * diagram.y
                )
            ))
            group.add(self.dwg.rect(
                (0, 0),
                (size * diagram.width, 2 * size * diagram.height),
                fill='white', stroke='black')
            )
            texts = diagram.text.get()
            for text in texts:
                group.add(self.dwg.text(
                    text=texts[text][1],
                    dx=[texts[text][0] * size ],
                    dy=[text * size * 2],
                    textLength=len(texts[text][1]) * size
                ))
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
