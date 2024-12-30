# TODO missing:
#  letters links,
#  search
#    w/wo title
#    w/ NLP tools
#  static pages,
#  verify and clean dict_check.docx,
#  clean TEMP and redundant files here,
#  backup backend,
# DOCX!!!   pip install python-docx
# pip install flair==0.13.0 scikit-learn==1.3.2 pandas==2.1.2 xgboost==2.0.3 joblib==1.3.2 scipy==1.12 rftokenizer


# TODO check TODOs in OLD-main.py
# TODO fix_links
# TODO htmler.add_footnote_to_output(id, footnote.paragraphs)
# TODO search_index
# TODO get_heading_type
# TODO update to modern Python

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
