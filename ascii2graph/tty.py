from .parser import AsciiParser
from .creator import PictureCreator

class TTYInterface:
    def __init__(self, test=False):
        pass

    def convert(self, input_file=None, output_file=None):
        ascii_parser = AsciiParser(open(input_file, 'r').readlines())
        picture_creator = PictureCreator(output_file)
        picture_creator.create(ascii_parser, size=10)
