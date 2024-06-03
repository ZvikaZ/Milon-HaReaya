# TODO check TODOs in OLD-main.py
# TODO fix_links
# TODO htmler.add_footnote_to_output(id, footnote.paragraphs)
# TODO search_index
# TODO get_heading_type

from helpers import create_dirs
from parse import parse
from db_updater import adapt_and_upload

# doc_file_name = 'dict_few.docx'
# doc_file_name = 'dict_check.docx'
doc_file_name = 'dict_short.docx'


# doc_file_name = 'dict_footnotes.docx'
# doc_file_name = 'מילון הראיה.docx'


create_dirs()
adapt_and_upload(parse(doc_file_name))
