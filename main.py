# -*- coding: utf-8 -*-
""" Currently, this is the 'main' module of this project.
By default, it parses 'dict.docx' (that contains Milon HaReaya's source Word file,
creates 'html_docs_l' - internal representation of all the Milon,
'subjects_db' which is used for searching (and is written as JSON file for the JS)
and then creates 'output/' with a working HTML/CSS/JS site, and zips it to 'milon.zip'

If 'secret.py' exists, it then uploads the .zip file to PhoneGap Build, waits for the .apk
to be ready, downloads it (to output/) and pushes everything (automatically) to Google Play.
"""

# TODO: Investigate "Intel Crosswalk" ARM/Intel implications

# TODO: Wrap each definition with <div> tag
# TODO: change 'is_prev_subject(..)' to correctly handle "Toar Shem Tov" - should be more freely checking
# TODO: "Yoru" - sizes changing
# TODO: otiyot - stam font
# TODO: pagination at end
# TODO: subject_light vs sub-subjet_light - wait for Rav's response

# TODO: "Mishkan UMikdash" - "Korbanot" - "Par" - some are not subjects, and one is a long link
# TODO: subjects size in Mehkarim
# TODO: references numbering
# TODO: search "Natziv" not working
# TODO: Or HaGaluy (see check.docx)
# TODO: Yud and Lamed in Psukim
# TODO: splitted bubject, like "אמר לו הקדוש ברוך הוא (לגבריאל° שבקש להציל את אברהם־אבינו° מכבשן האש) אני יחיד בעולמי והוא יחיד בעולמו, נאה ליחיד להציל את היחיד"

# TODO: circles shouldn't be part of subjects (and what about parentheses?)
# TODO: decrease size of app
# TODO: breadcrumbs
# TODO: "Mehkarim" - make links, check styles!
# TODO: Change "opening_abbrev.html" styling
# TODO: handle footnotes' styles
# TODO: "Ayen", "Re'e" - see mail from 22.1.16
# TODO: "all subjects" page

# TODO: make headings to links
# TODO: save current location (and history?, with back and forward?) - use HTML5 local storage
# TODO: search - results page - write first words of definition
# TODO: add letters to TOC
# TODO: make smarter links on circles ('Oneg' with and w/o Vav, 'zohama' with Alef or He, etc.)
# TODO: increase/decrease font size
# TODO: make definition in new line? (without ' - ')

# TODO: replace menu with Bootstrap style menu
# TODO: Make index.html's links clickable, or copyable
# TODO: Split this file...
# TODO: better icon
# TODO: iphone?
# TODO: GUI

# remember:
# http://stackoverflow.com/questions/10752055/cross-origin-requests-are-only-supported-for-http-error-when-loading-a-local

# hopefully, I will get a new delivery of python-docx supporting szCs
# (see https://github.com/python-openxml/python-docx/issues/248 )
# in the meanwhile, I've hacked it locally
import sys
sys.path.insert(0, r'C:\Users\zharamax\PycharmProjects\python-docx')
sys.path.insert(0, r'C:\Users\sdaudi\Github\python-docx')

import docx
import docx_fork_ludoo
import zipfile
import os
import shutil
import json
import copy

import build_phonegap
import upload_google_play
from text_segments import MilonTextSegments as TS, fake
import text_segments as ts
from docx2abstract_doc import *
import docxparser as parse
import build_html as bhtml
import build_latex as blatex
import multi_build as mbuild


#process = "Full"
#process = "APK"
process = "ZIP"

if process == "Full":
    doc_file_name = 'dict.docx'
    create_html = True
    #create_latex = True
    create_latex = False
else:
    #doc_file_name = 'dict_few.docx'
    #doc_file_name = 'dict_check.docx'
    #doc_file_name = 'dict_short.docx'
    doc_file_name = 'dict.docx'

    create_html = True
    create_latex = False


parser = parse.MilonDocxParser(doc_file_name, 'output/debug.txt')

#####################################################################################
## create the builders ##############################################################
html_builder = bhtml.MilonHTMLBuilder('input_web', 'output')
html_builder.set_word_doc_footnotes(parser.word_doc_footnotes)
latex_builder = blatex.MilonLatexBuilder('input_tex', 'tex')
#####################################################################################

#####################################################################################
## add the builders to the multi-builder ############################################
## this is where you should comment-out the builders you don't need #################
builder = mbuild.MilonMultiBuilder()
builder.addBuilder(html_builder)
#builder.addBuilder(latex_builder)
#####################################################################################

# Here starts the action!
builder.start()
for para, footnotes, size_kind in parser.paragraphs():
    builder.add(para, footnotes, size_kind)

parser.finish()
builder.finish()


with zipfile.ZipFile("milon.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    os.chdir("output")
    for dirname, subdirs, files in os.walk("."):
        # avoid creating 'output' directory as first hierrarchy
        # suddenly causes problem with phonegap - makes garbages APKs...
        zf.write(dirname)
        for filename in files:
            if not 'debug' in filename:
                zf.write(os.path.join(dirname, filename))
    print "Created milon.zip"
os.chdir("..")

shutil.move("milon.zip", "output/")

if process != "ZIP":
    try:
        build_phonegap.push_to_phonegap("output/milon.zip")
        if process == "Full":
            upload_google_play.main()
    except Exception as e:
        print "Build process failed!"
        print e