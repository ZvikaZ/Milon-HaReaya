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
import re
import zipfile
import os
import shutil
import json
import copy
import subprocess

import build_phonegap
import upload_google_play
from text_segments import MilonTextSegments as TS, fake
import text_segments as ts
from docx2abstract_doc import *
import docxparser as parse
import fixes
import build_html as bhtml
import build_latex as blatex


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


word_doc = docx.Document(doc_file_name)
word_doc_footnotes = docx_fork_ludoo.Document(doc_file_name)

try:
    shutil.rmtree("output")
except:
    pass

try:
    shutil.rmtree("tex")
except:
    pass

os.mkdir("tex")
os.mkdir("output")
os.mkdir("output/html_demos-gh-pages")

os.chdir("input_web")
for (f) in (
    'config.xml',
    'icon.png',
    'style.css',
    'html_demos-gh-pages/footnotes.css',
    'html_demos-gh-pages/footnotes.js',
    'milon.js',
    'index.html',
    'opening_abbrev.html',
    'opening_haskamot.html',
    'opening_intros.html',
    'opening_signs.html',
    'search.html',
):
    shutil.copyfile(f, os.path.join("../output", f))

for (d) in (
    'bootstrap-3.3.6-dist',
    'bootstrap-rtl-3.3.4',
    'jquery',
):
    shutil.copytree(d, os.path.join("../output", d))

os.chdir("../input_tex")
for (f) in (
    "milon.tex",
    "polythumbs.sty",
):
    shutil.copyfile(f, os.path.join("../tex", f))
os.chdir("../")

blatex.open_latex()
# Here starts the action!
# TODO - we should get all the code up to here OUT of this file into modules
with open('output/debug.txt', 'w') as debug_file:
    # para = []
    for (paragraph, footnote_paragraph) in zip(word_doc.paragraphs, word_doc_footnotes.paragraphs):
        if paragraph.text.strip():
            para, size_kind, footnotes = parse.parse_runs(paragraph, footnote_paragraph, debug_file)
            para.append((TS.newLine, "\n"))
            # parser until here
            para = fixes.analyze_and_fix(para)
            # fixes until here
            if create_html:
                #html_doc = bhtml.add(para, footnotes, size_kind)
                bhtml.add(para, footnotes, size_kind)
            if create_latex:
                blatex.add_to_latex(para)
            # builder(s) until here
        else:
            try:
                # if there is a 'html_doc' - add to id new_line for the paragraph ended
                # if there isn't - it doesn't matter, we're just at the beginning - ignore it
                para = []
                para.append((TS.newLine, "\n"))
                if create_html:
                    bhtml.begin_add(para, size_kind)
                if create_latex:
                    blatex.add_to_latex(para)
            except:
                pass

# TODO move this block to build_html
if create_html:
    bhtml.finish(word_doc_footnotes)

if parse.unknown_list:
    print "\n\nMissing:"
    print parse.unknown_list

# TODO move this block to build_latex
if create_latex:
    blatex.close_latex()

with open('output/subjects_db.json', 'wb') as fp:
    s = json.dumps(bhtml.subjects_db, encoding='utf8')
    fp.write("data = " + s)

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