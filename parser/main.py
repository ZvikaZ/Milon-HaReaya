# TODO check TODOs in OLD-main.py
# TODO fix_links
# TODO htmler.add_footnote_to_output(id, footnote.paragraphs)
# TODO search_index
# TODO get_heading_type

import shutil
import os

from parse import parse
from jsoner import create_json

# doc_file_name = 'dict_few.docx'
# doc_file_name = 'dict_check.docx'
doc_file_name = 'dict_short.docx'


# doc_file_name = 'dict_footnotes.docx'
# doc_file_name = 'מילון הראיה.docx'

def create_dirs():
    try:
        shutil.rmtree("output")
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree("tex")
    except FileNotFoundError:
        pass

    os.mkdir("output")
    os.mkdir("tex")


create_dirs()
create_json(parse(doc_file_name))
