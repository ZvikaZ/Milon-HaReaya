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
import dominate
import dominate.tags as tags
import re
import zipfile
import os
import shutil
import HTMLParser
import json
import copy
import subprocess

import build_phonegap
import upload_google_play
from text_segments import MilonTextSegments as TS, fake
import text_segments as ts
from docx2abstract_doc import *
import fixes
# from sizes import Sizes
import sizes
import build_html as bhtml
import build_latex as blatex

html_parser = HTMLParser.HTMLParser()

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


# support old and new version of docx
# new is preferred, because, well, it's new...
# old is preferred because I'm using a branch with footnotes support
def run_style_id(run):
    try:
        return run.style.style_id
    except:
        if run.style:
            return run.style
        else:
            return 'DefaultParagraphFont'

unknown_list = []

def is_footnote_recurrence(run, type):
    # a number in superscript, that's not defined as a footnote
    return \
        run.element.rPr.vertAlign is not None \
        and type != TS.footnote \
        and run.text.strip().isdigit() \
        and run.element.rPr.vertAlign.values()[0] == 'superscript'


######################################################################
### latex ############################################################
######################################################################
def open_latex():
    pass
    # nothing to do here...



def latex_type(type):
    if type == TS.subjectNormal:
        return u"ערך"
    elif type in (TS.subSubjectNormal, TS.subjectNormal, fake(TS.subjectSmall), fake(TS.subSubjectNormal)):
        return u"משנה"
    elif type in (TS.definitionNormal, "fake_subject_small_normal"):
        return u"הגדרה"
    elif type == TS.sourceNormal:
        return u"מקור"
    elif type == TS.subSubjectSmall:
        return u"צמשנה"
    elif type == TS.definitionSmall:
        return u"צהגדרה"
    elif type == TS.sourceSmall:
        return u"צמקור"
    elif type == TS.footnote:
        return TS.footnote    #TODO: improve footnote
    elif type == TS.MeUyan:
        return u"מעוין"
    #elif type == "DefaultParagraphFont":
    #    return #TODO: what??
    else:
        return u"תקלה"



latex_new_lines_in_raw = 0
def add_to_latex(para):
    global latex_new_lines_in_raw
    data = ""
    for (i, (type, text)) in enumerate(para):
        if 'heading' in type and text.strip():
            data += "\\end{multicols}\n"

            # TODO: adjust headings
            if type == 'heading_title':
                data += ("\\chapter{%s}" % text)
                data += ("\\addPolythumb{%s}" % text)
            elif type == 'heading_section':
                data += ("\\chapter{%s}" % text)
                data += ("\\addPolythumb{%s}" % text)
            elif type == 'heading_sub-section-bigger':
                data += ("\\subsection{%s}" % text)
            elif type == 'heading_sub-section':
                data += ("\\subsection{%s}" % text)
            elif type == 'heading_letter':
                data += ("\\subsubsection{%s}" % text)
                data += ("\\replacePolythumb{%s}" % text)

            data += "\n"
            if 'letter' in type:
                data += u"\\fancyhead[CO]{אות %s}\n" % text
            else:
                data += "\\fancyhead[CE,CO]{%s}\n" % text

            data += "\\begin{multicols}{2}\n"


        elif type == TS.newLine:
            latex_new_lines_in_raw += 1
            if latex_new_lines_in_raw == 1:
                if data:
                    data += ("\\\\")
            elif latex_new_lines_in_raw == 2:
                data += ("\n\n")
            else:
                pass

        elif type == TS.footnote:
            id = int(text)
            footnote = word_doc_footnotes.footnotes_part.notes[id + 1]
            assert footnote.id == id
            foot_text = ""
            for (para) in footnote.paragraphs:
                foot_text += para.text

            data += ("\\%s{%s}" % (type, foot_text))

        # elif is_subject(para, i):
        #     if not is_prev_subject(para, i):
        #         # tags.p()
        #         #tags.br()
        #         pass
        #     subject(html_doc, type, text)
        else:
            # regular(type, text)
            data += ("\\%s{%s}" % (latex_type(type), text))

        if type != TS.newLine:
            latex_new_lines_in_raw = 0
                
    with open("tex\content.tex", 'a') as latex_file:
        latex_file.write(data.encode('utf8'))

def close_latex():
    os.chdir("tex")
    # twice because of thumb-indices
    subprocess.call(['xelatex', 'milon.tex'])
    subprocess.call(['xelatex', 'milon.tex'])
    os.startfile("milon.pdf")
    os.chdir("..")



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

temp_l = []
def bold_type(s, type, run):
    if type == TS.definitionNormal:
        return TS.subjectSmall
    elif type == TS.sourceNormal and run.style.style_id == "s03":
        return TS.subSubjectSmall
    elif type == TS.definitionSmall and run.style.style_id == "s05":
        return TS.subSubjectSmall
    elif type == TS.sourceNormal and run.style.style_id == "DefaultParagraphFont" and run.font.size == 139700:
        return TS.subjectNormal
    elif type == TS.sourceNormal and run.style.style_id == "DefaultParagraphFont" and run.font.size != 139700:
        return TS.subSubjectNormal
    elif type == TS.unknownLight and run.style.style_id == "s04" and run.font.size == 114300:
        return TS.subjectLight
    elif type == TS.unknownLight and run.style.style_id == "s04" and run.font.size == 101600:
        return TS.subSubjectLight
    elif type == TS.definitionLight and run.style.style_id == "s12" and run.font.size == 101600:
        return TS.subSubjectLight
    elif type == TS.definitionLight and run.style.style_id == "s12" and run.font.size is None:
        # TODO - verify that it's always OK
        return TS.subSubjectLight
    elif type == TS.sourceNormal:
        print "Strange TS.sourceNormal bold!"
    elif 'subject' in type or 'heading' in type:
        return type
    elif run.text.strip() in (u"◊", "-", ""):
        return type
    else:
        if type not in temp_l:
            print "Unexpected bold!", type
            print s, type, run.text, run.font.size
            assert False
            temp_l.append(type)
        return type


def parse_runs(runs, footnote_runs, debug_file):
    size_kind = None # when the return statment is changed, this line should be deleted
    para = []
    debug_file.write("\n\nNEW_PARA:\n------\n")
    for (run, footnote_run) in zip(paragraph.runs, footnote_paragraph.runs):
        s = "!%s.%s:%s$" % (run.style.style_id, docxCode2segType.get(run_style_id(run), run_style_id(run)), run.text)
        # print "!%s:%s$" % (docxCode2segType.get(run.style.style_id, run.style.style_id), run.text)
        debug_file.write(s.encode('utf8'))
        type = docxCode2segType.get(run_style_id(run), TS.unknown)

        if run.font.size and run.text.strip():
            size_kind = sizes.match(run.font.size)
            if size_kind == TS.unknown:
                print "!%s. Size: %d, Bool: %s, %s:%s$" % (size_kind, run.font.size, run.bold, type, run.text)
            if size_kind not in ('normal', TS.unknown):
                type = size_kind

        if 'unknown' in type and run.text.strip():
            type = fixes.fix_unknown(run)

        elif type == "DefaultParagraphFont":
            type = fixes.fix_DefaultParagraphFont(run)
            # print paragraph.style.style_id, run.bold, run.font.size, s

        elif run.bold:
            type = bold_type(s, type, run)

        # single run & alignment is CENTER and ...-> letter heading
        elif len(paragraph.runs) == 1 and paragraph.alignment is not None and int(paragraph.alignment) == 1\
                and "heading" not in type and run.text.isalpha():
            # print "NEW heading letter!", s
            size_kind = "heading_letter"
            type = size_kind


        try:
            if run.element.rPr.szCs is not None and run.text.strip():
                type = fixes.fix_sz_cs(run, type)

            if run.element.rPr.bCs is not None and run.text.strip():
                type = fixes.fix_b_cs(run, type)

            # NOTE: this footnote number need no fix.
            # it is a recurrance, therefore it has no id.
            if is_footnote_recurrence(run, type):
                type = TS.footnoteRec
    
        except:
            pass


        para.append((type, run.text))

        if type == TS.unknown:
            if run_style_id(run) not in unknown_list:
                unknown_list.append(run_style_id(run))
                print paragraph.text
                s = "\nMissing: !%s:%s$\n\n" % (run_style_id(run), run.text)
                print s
                debug_file.write(s.encode('utf8'))


        try:
            # if run.footnote_references:
            footnote_references = footnote_run.footnote_references
            if footnote_references:
                for (note) in footnote_references:
                    if create_html:
                        html_doc.footnote_ids_of_this_html_doc.append(note.id)
                        relative_note_id = note.id - html_doc.footnote_ids_of_this_html_doc[0] + 1
                        # print TS.footnote, relative_note_id
                        para.append((TS.footnote, str(relative_note_id)))
                    elif create_latex:
                        #TODO:  we have a problem here!
                        #what happens in case of both html & latex??
                        para.append((TS.footnote, str(note.id)))

        except:
            print "Failed footnote_references"
            raise

    return para, size_kind # this should be changed. size_kind shouldn't be returned and moved to other functions. it makes no sence.

open_latex()
# Here starts the action!
# TODO - we should get all the code up to here OUT of this file into modules
with open('output/debug.txt', 'w') as debug_file:
    for (paragraph, footnote_paragraph) in zip(word_doc.paragraphs, word_doc_footnotes.paragraphs):
        if paragraph.text.strip():
            para, size_kind = parse_runs(paragraph.runs, footnote_paragraph.runs, debug_file)

            para.append((TS.newLine, "\n"))
            # parser until here
            para = fixes.analyze_and_fix(para)
            # fixes until here
            if create_html:
                html_doc = bhtml.add(para, size_kind)
                # html_doc = get_active_html_doc(para)
                # add_to_output(html_doc, para, size_kind)
            if create_latex:
                add_to_latex(para)
            # builder(s) until here
        else:
            try:
                # if there is a 'html_doc' - add to id new_line for the paragraph ended
                # if there isn't - it doesn't matter, we're just at the beginning - ignore it
                para = []
                para.append((TS.newLine, "\n"))
                if create_html:
                    html_doc = html_docs_l[-1]
                    add_to_output(html_doc, para, size_kind)
                if create_latex:
                    add_to_latex(para)
            except:
                pass

# TODO move this block to build_html
if create_html:
    bhtml.finish(word_doc_footnotes)
    '''
    bhtml.html_docs_l = bhtml.fix_links(bhtml.html_docs_l)
    bhtml.add_menu_to_apriory_htmls(bhtml.html_docs_l)

    for (html_doc) in bhtml.html_docs_l:
        bhtml.close_html_doc(html_doc, word_doc_footnotes)
'''

if create_latex:
    close_latex()

with open('output/subjects_db.json', 'wb') as fp:
    s = json.dumps(bhtml.subjects_db, encoding='utf8')
    fp.write("data = " + s)


if unknown_list:
    print "\n\nMissing:"
    print unknown_list


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