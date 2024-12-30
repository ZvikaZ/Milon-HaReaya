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

import argparse

from helpers import create_dirs
from parse import parse
from db_updater import adapt_and_upload



def create_pdf(parsed_data):
    # Placeholder for the create_pdf functionality
    print("Creating PDF...")
    # Add PDF creation logic here

def main():
    parser = argparse.ArgumentParser(description="Transpiles the Milon HaReaya word file to a Web site or to a PDF.")
    parser.add_argument('--web', action='store_true', help='Update the Milon web site')
    parser.add_argument('--pdf', action='store_true', help='Create a PDF')
    parser.add_argument('--file', type=str, default='dict_short.docx',
                        # default = 'dict_few.docx'
                        # default = 'dict_check.docx'
                        # default = 'dict_footnotes.docx'
                        # default = 'מילון הראיה.docx'
                        help='Path to the DOCX file (default: %(default)s)')
    args = parser.parse_args()

    if not (args.web or args.pdf):
        parser.error('At least one of --web or --pdf must be specified.')


    create_dirs()
    parsed_data = parse(args.file)

    if args.web:
        adapt_and_upload(parsed_data)
    if args.pdf:
        create_pdf(parsed_data)

if __name__ == "__main__":
    main()
