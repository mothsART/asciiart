import os

from ascii2graph.parser import AsciiParser
from ascii2graph.creator import PictureCreator


def get_path(dir_name, file_name):
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, dir_name, file_name)


def paths_to_str(tmpdir, input_filename, output_filename):
    input_path = get_path('input', input_filename)
    ascii_parser = AsciiParser(open(input_path, 'r').readlines())
    output_path = get_path('output', output_filename)

    tmpfile_path = os.path.join(str(tmpdir), output_filename)

    picture_creator = PictureCreator(tmpfile_path)
    picture_creator.create(ascii_parser, size=10)

    tmp_str = open(tmpfile_path, 'r').read()
    output_str = open(output_path, 'r').read()
    return tmp_str, output_str


def test_one_diagram(tmpdir):
    """ Test minimal diagram : rectangle with inner text """
    str_to_compare = paths_to_str(
        tmpdir, 'one_diagram.txt', 'one_diagram.svg'
    )
    assert str_to_compare[0] == str_to_compare[1]


def test_styling_text(tmpdir):
    """ Test minimal text with styling (bold) """
    str_to_compare = paths_to_str(
        tmpdir, 'styling_text.txt', 'styling_text.svg'
    )
    assert str_to_compare[0] == str_to_compare[1]


def test_heritage(tmpdir):
    """ Test a set of diagrams : several in another :
    must be interpretate as a hierarchical tree """
    pass
