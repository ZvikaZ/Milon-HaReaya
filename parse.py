# -*- coding: utf-8 -*-
""" Currently, this is the 'main' module of this project.
By default, it parses 'dict.docx' (that contains Milon HaReaya's source Word file,
creates 'html_docs_l' - internal representation of all the Milon,
'subjects_db' which is used for searching (and is written as JSON file for the JS)
and then creates 'output/' with a working HTML/CSS/JS site, and zips it to 'milon.zip'

If 'secret.py' exists, it then uploads the .zip file to PhoneGap Build, waits for the .apk
to be ready, downloads it (to output/) and pushes everything (automatically) to Google Play.
"""

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
from text_segments import MilonTextSegments as TS
from docx2abstract_doc import *

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
    doc_file_name = 'dict_check.docx'
    #doc_file_name = 'dict_short.docx'
    #doc_file_name = 'dict.docx'

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


# if the actual size is greater
class Sizes:
    my_dict = {
        381000: 'heading_title',
        330200: 'heading_section',              # e.g., "Tora"
        279400: 'heading_sub-section-bigger',   # e.g., "Mehkarim Beurim"
        215900: 'heading_sub-section',          # e.g., "Avraham Yitzhak VeYaakov"
        177800: 'heading_letter',
        165100: 'normal',               # 152400
    }

    # yeah, it's not nice and programmaticish to have this twice
    # but it's more efficient :)
    normal = 165100

    def match(self, size):
        if size > self.normal:
            return self.my_dict.get(size, "unknown")
        else:
            return 'normal'

    def get_heading_type(self, kind):
        if kind == 'heading_title':
            return tags.h1
        elif kind == 'heading_section':
            return tags.h2
        elif kind == 'heading_sub-section-bigger':
            return tags.h3
        elif kind == 'heading_sub-section':
            return tags.h4
        elif kind == 'heading_letter':
            return tags.h5

sizes = Sizes()

unknown_list = []

# dictionary mapping subjects to list of pointers
# each pointer is a tuple of (subject, html_doc's section name, url)
subjects_db = {}

def calc_subject_id(text_orig, cnt):
    # subject_id = "subject_%d" % len(subjects_db)
    text = text_orig.replace(" ", "-")
    if cnt == 0:
        return text
    else:
        return "%s%d" % (text, cnt)


def subject(html_doc, type, text):
    clean_text = clean_name(text.strip())
    new_subject_l = subjects_db.get(clean_text, [])
    subject_id = calc_subject_id(text.strip(), len(new_subject_l))
    new_subject_l.append((text.strip(), html_doc.section, "%s.html#%s" % (html_doc.index, subject_id)))
    subjects_db[clean_text] = new_subject_l

    with tags.span(text, id=subject_id):
        tags.attr(cls=type)

    # with tags.span(tags.a(text, href="#%s" % text.strip(), id=text.strip())):
    #     tags.attr(cls=type)

def regular(type, text):
    if type in [TS.footnote, TS.footnoteRecc]:
        with tags.a("(%s)" % text.strip()):
            tags.attr(cls="ptr")
    else:
        if "\n" in text:
            print "New:", text
        if u"°" in text:
            href = re.sub(u"°", "", text)
            href = re.sub(u"־", " ", href)
            with tags.span(tags.a(text, href="#"+href)):
                tags.attr(cls=type)
        else:
            with tags.span(text):
                tags.attr(cls=type)

def is_footnote_recurrence(run, type):
    # a number in superscript, that's not defined as a footnote
    return \
        run.element.rPr.vertAlign is not None \
        and type != TS.footnote \
        and run.text.strip().isdigit() \
        and run.element.rPr.vertAlign.values()[0] == 'superscript'

def is_subject(para, i, next=False):
    type, text = para[i]
    # print "is? ", type, text.strip()
    # if 'subject' in type and not re.search(r"\w", text, re.UNICODE):
    #     print "!", text
    # print "is?", type, text, i, ('subject' in type and re.search(r"\w", text, re.UNICODE))

    # if 'subject' in type and re.search(r"\w", text, re.UNICODE) and i>0:
    #     p_type, p_text = para[i-1]
    #     print "?", i-1, p_type, p_text
    return 'subject' in type and re.search(r"\w", text, re.UNICODE) and 'fake' not in type

def is_prev_subject(para, i):
    try:
        return (is_subject(para, i-2) and
                (para[i-1][1].replace('"','').strip() == "-") or (para[i-1][0] == "footnote"))
    except:
        return False

def is_prev_newline(para, i):
    try:
        return para[i-1][0] == "new_line" or (para[i-2][0] == "new_line" and para[i-1][1] == "")
    except:
        return False

def is_prev_meuyan(para, i):
    try:
        return para[i-1][0] == "s02Symbol"
    except:
        return False



def make_sub_subject(subj):
    if subj == TS.subjectSmall:
        return TS.subSubjectNormal
    else:
        return subj

def is_subject_small_or_sub_subject(s):
    return s in [TS.subjectSmall, TS.subSubjectNormal]

def analyze_and_fix(para):
    # unite splitted adjacent similar types
    prev_type, prev_text = None, ""
    new_para = []
    for (raw_type, text_raw) in para:
        text = text_raw.replace("@", "")
        if text == u"◊":
            type = "s02Symbol"
        else:
            type = raw_type
        if prev_type:
            if (type == prev_type) or \
                    (is_subject_small_or_sub_subject(type) and is_subject_small_or_sub_subject(prev_type)) or \
                    (prev_type != "footnote" and text.strip() in ("", u"°", u"־", ",")):
                prev_text += text
            else:
                new_para.append((prev_type, prev_text))
                prev_type, prev_text = type, text
        else:
            prev_type, prev_text = type, text
    new_para.append((prev_type, prev_text))

    # make new_lines stand on their own
    para = new_para
    new_para = []
    for (type, text) in para:
        lines = text.split("\n")
        if len(lines) > 1:
            for (i, line) in enumerate(lines):
                if line:
                    new_para.append((type, line))
                if i+1 < len(lines):
                    new_para.append(("new_line", "\n"))
        else:
            new_para.append((type, text))

    # fix wrong subjects
    para = new_para
    new_para = []
    for (index, (type, text)) in enumerate(para):
        # if 'subject' in type:
        if is_subject(para, index):
            # real subject is either:
            # first
            # after new_line and empty
            # after subject,"-"
            # after Meuyan
            if (index == 0) or (is_prev_newline(para, index)) or (is_prev_meuyan(para, index)):
                new_para.append((type, text))
            elif (is_prev_subject(para, index)):
                new_para.append((make_sub_subject(type), text))
            elif new_para[index-1][0] in (TS.subSubjectNormal, TS.subjectSmall):
                new_para.append((make_sub_subject(type), text))
            else:
                new_para.append(("fake_"+type, text))
        elif 'subject' in type:
            # it's got a subject, but 'is_subject' failed
            new_para.append(("fake_"+type, text))
        else:
            new_para.append((type, text))

    # fix wrong 'source's
    para = new_para
    new_para = []
    source_pattern = re.compile(r"(\s*\[.*\]\s*)")
    for (type, text) in para:
        if type == TS.sourceNormal:
            small = False
            for (chunk) in source_pattern.split(text):
                if source_pattern.match(chunk):
                    if small:
                        new_para.append((TS.sourceSmall, chunk))
                    else:
                        new_para.append((type, chunk))
                elif chunk != "":
                    new_para.append((TS.definitionSmall, chunk))
                    small = True
                # re.split(r"(\[.*\])", s)
        else:
            new_para.append((type, text))

    # make links from circles - °
    para = new_para
    new_para = []
    pattern = re.compile(u"([\S־]*\S+°)", re.UNICODE)
    for (type, text) in para:
        # don't do this for subjects - it complicates their own link name...
        if u"°" in text and 'subject' not in type:
            for (chunk) in pattern.split(text):
                new_para.append((type, chunk))
        else:
            new_para.append((type, text))


    # fix new lines inside headings
    para = new_para
    new_para = []
    ignore_new_line = False
    for (type, text) in para:
        if 'heading' in type:
            ignore_new_line = True
            new_para.append((type, text))
        elif type == "new_line" and ignore_new_line:
            pass
        else:
            new_para.append((type, text))


    # scan for 'empty subjects' ...
    has_subject = False
    has_definition = False
    for (type, text) in para:
        if 'subject' in type and 'fake' not in type and text.strip():
            has_subject = True
            has_definition = False
        elif 'definition' in type:
            has_definition = True

    # ... and fix 'em if required
    if has_subject and not has_definition:
        # empty subject
        #TODO - might be caused by 'heading' interpreted as subject
        para = new_para
        new_para = []
        for (type, text) in para:
            if 'subject' in type and 'fake' not in type:
                new_para.append(('fake_'+type, text))
            else:
                new_para.append((type, text))


    with open('output/debug_fix.txt', 'a') as debug_file:
        debug_file.write("---------------\n")
        for (type, text) in new_para:
            s = "%s:%s.\n" % (type, text)
            debug_file.write(s.encode('utf8') + ' ')

    # fix
    return new_para

# return True if updated
def update_values_for_href(child, href):
    values = subjects_db.get(href)
    #TODO: support showing more than 1 result
    if values is None:
        return False
    if len(values) == 1:
        _, _, url = values[0]
        child.children[0]['href'] = url
        return True
    elif len(values) > 1:
        # # tuple of (subject, html_doc's section name, url)
        # subject, section, url = values[]
        child.children[0]['href'] = "search.html?"+href
        return True
    else:
        assert False

def update_href_no_link(child):
    assert len(child.children[0].children) == 1
    text = html_parser.unescape(child.children[0].children[0])
    child.children[0] = tags.span(text)

def fix_links(html_docs_l):
    # fix outbound links
    print "Fixing links"
    for (doc) in html_docs_l:
        for (child) in doc.body.children[0].children:
            if 'definition' in child.attributes.get('class', ()):
                href = ""
                try:
                    href = child.children[0].attributes.get("href")
                except AttributeError as e:
                    pass

                # it's a link - try to update it
                if href:
                    # first, strip it of weird chars
                    try:
                        href = clean_name(href)

                        updated = False
                        if update_values_for_href(child, href):
                            updated = True
                        else:
                            if href[0] in (u"ה", u"ו", u"ש", u"ב", u"כ", u"ל", u"מ"):
                                updated = update_values_for_href(child, href[1:])
                        if not updated:
                            # failed to update - it's not a real link...
                            update_href_no_link(child)

                    except Exception as e:
                        pass
                        print e, "Exception of HREF update", href
                        #TODO - investigate why it happens? (it's a single corner case, I think)


    def sorter(html_doc):
        if html_doc.name in [u"ערכים כלליים",]:
            return "FIRST"
        if html_doc.name in [u"נספחות",]:
            return u"תתתתתתתתתת"    #last
        else:
            return html_doc.name

    # update sections menu
    for (doc) in html_docs_l:
        letters_l = []

        # content_menu = doc.body.children[0].children[1].children[0].children[0].children[-1].children[0].children[1]
        content_menu = doc.body.children[0].children[1].children[0].children[1].children[-1]
        assert content_menu['class'] == 'dropdown-menu dropdown-menu-left scrollable-menu'

        with content_menu:
            with tags.li():
                tags.a(u"אודות", href="index.html")
            with tags.li():
                tags.a(u"הקדמות", href="opening_intros.html")
            with tags.li():
                tags.a(u"הסכמות", href="opening_haskamot.html")
            with tags.li():
                tags.a(u"קיצורים", href="opening_abbrev.html")
            with tags.li():
                tags.a(u"סימנים", href="opening_signs.html")
            # if you add more entries here, please update add_menu_to_apriory_htmls(..)
            with tags.li():
                tags.attr(cls="divider")

            sorted_html_docs_l = sorted(html_docs_l, key=sorter)

            for (html_doc) in sorted_html_docs_l:
                # Only if this a 'high' heading, and not just a letter - include it in the TOC
                if html_doc.name != "NEW_LETTER":
                    with tags.li():
                        tags.a(html_doc.name, href=str(html_doc.index)+".html")
                        if doc.section == html_doc.section:
                            tags.attr(cls="active")
                else:
                    # it's a letter - if it's related to me, save it
                    if doc.section == html_doc.section:
                        letters_l.append(html_doc)

        with doc.body.children[-1]:
            assert doc.body.children[-1]['class'] == 'container-fluid'
            with tags.ul():
                tags.attr(cls="pagination")
                for (html_doc) in letters_l:
                    tags.li(tags.a(html_doc.letter, href=str(html_doc.index)+".html"))



    return html_docs_l

new_lines_in_raw = 0
def add_to_output(html_doc, para):
    global new_lines_in_raw
    # we shouldn't accept empty paragraph (?)
    assert len(para) > 0

    with html_doc.body.children[-1]:
        assert html_doc.body.children[-1]['class'] == 'container-fluid';
        for (i, (type, text)) in enumerate(para):
            if 'heading' in type and text.strip():
                # tags.p()
                # tags.p()
                heading = sizes.get_heading_type(size_kind)
                print type, text
                heading(text)
            elif type == "new_line":
                new_lines_in_raw += 1
                if new_lines_in_raw == 1:
                    tags.br()
                elif new_lines_in_raw == 2:
                    tags.p()
                else:
                    pass
            elif is_subject(para, i):
                if not is_prev_subject(para, i):
                    # tags.p()
                    #tags.br()
                    pass
                subject(html_doc, type, text)
            else:
                regular(type, text)

            if type != "new_line":
                new_lines_in_raw = 0

        # tags.br()

def add_footnote_to_output(paragraphs):
    text = ""
    for (para) in paragraphs:
        text += para.text
    tags.li(text)


def fix_sz_cs(run, type):
    result = type
    szCs = run.element.rPr.szCs.attrib.values()[0]
    if szCs == "20" and 'subject' in type:
        if run.style.style_id == "s01":
            s = "!Fixed!szCs=%s:%s." % (szCs, run.text)
            # print s
            debug_file.write(s.encode('utf8') + ' ')
            return TS.subjectSmall
    elif szCs == "22" and type == TS.definitionNormal:
        return TS.subjectNormal
    elif szCs == "16" and type == TS.sourceNormal:
        return TS.sourceSmall
    else:
        pass
    return result

def fix_b_cs(run, type):
    result = type
    try:
        bCs = run.element.rPr.bCs.attrib.values()[0]
        if bCs == "0" and 'subject' in type:
            if type in (TS.subjectSmall, TS.subSubjectNormal):
                return TS.definitionNormal
            else:
                pass
                # print "Unknown b_cs=0"
    except:
        pass
    return result

def fix_unknown(run):
    if run.font.size == 114300 and run.style.style_id == 's04':
        return TS.subjectLight
    elif run.font.size == 101600 and run.style.style_id == 's04' and run.font.cs_bold:
        return TS.subSubjectLight
    elif run.font.size == 101600 and run.style.style_id == 's04' and not run.font.cs_bold:
        return TS.definitionLight
    elif run.font.size is None and run.style.style_id == 's04':
        return TS.definitionLight
    elif run.font.size == 88900 and run.style.style_id == 's04':
        return TS.sourceLight
    else:
        return TS.unknownLight


def fix_DefaultParagraphFont(run):
    # only if it's really a text
    if run.text.strip() and run.text.strip() not in ("-", "(", ")", "[", "]", "'", '"', ","):
        if run.font.size == 152400 and not run.bold:
            return TS.subjectNormal
        if run.font.size == 139700 and run.bold:
            return TS.subjectNormal
        elif run.font.size == 127000:
            return TS.definitionNormal
        elif run.font.size == 114300:
            return TS.sourceNormal
        elif run.font.size == 101600:
            return TS.sourceSmall
        elif run.font.size == 88900:
            return TS.sourceSmall
        elif run.font.size is None and run.bold:
            return TS.subSubjectNormal
        elif run.font.size is None and not run.bold:
            return TS.definitionNormal
        else:
            print "AH!", ":",run.text.strip(),".", run.font.size, run.bold
            assert False
    else:
        return TS.defaultParagraph

temp_l = []
def bold_type(s, type, run):
    if type == TS.definitionNormal:
        return TS.subjectSmall
    elif type == TS.sourceNormal and run.style.style_id == "s03":
        return 'sub-subject_small'
    elif type == "definition_small" and run.style.style_id == "s05":
        return 'sub-subject_small'
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


def open_html_doc(name, letter=None):
    html_doc = dominate.document(title=u"מילון הראיה")
    html_doc['dir'] = 'rtl'
    with html_doc.head:
        with tags.meta():
            tags.attr(charset="utf-8")
        with tags.meta():
            tags.attr(name="viewport", content="width=device-width, initial-scale=1")

        tags.script(src="jquery/dist/jquery.min.js")
        tags.link(rel='stylesheet', href='bootstrap-3.3.6-dist/css/bootstrap.min.css')
        tags.link(rel='stylesheet', href='style.css')
        tags.script(src="bootstrap-3.3.6-dist/js/bootstrap.min.js")
        tags.link(rel='stylesheet', href="bootstrap-rtl-3.3.4/dist/css/bootstrap-rtl.css")
        tags.link(rel='stylesheet', href='html_demos-gh-pages/footnotes.css')
        tags.script(src="milon.js")
        tags.script(src="html_demos-gh-pages/footnotes.js")
        tags.script(src="subjects_db.json")




    html_doc.footnote_ids_of_this_html_doc = []
    html_doc.name = name
    if letter:
        html_doc.letter = letter
        html_doc.section = html_docs_l[-1].section
    else:
        html_doc.section = name

    html_doc.index = len(html_docs_l) + 1
    with html_doc.body:
        with tags.div():
            tags.attr(cls="container-fluid")
            # TODO: call page_loaded to update saved URL also in other links
            tags.script("page_loaded('%s.html')" % html_doc.index)

            with tags.div():
                tags.attr(cls="fixed_top_left", id="menu_bar")
                with tags.div():
                    with tags.button(type="button"):
                        tags.attr(id="search_icon_button", type="button", cls="btn btn-default")
                        with tags.span():
                            tags.attr(cls="glyphicon glyphicon-search")
                    with tags.span():
                        tags.attr(cls="dropdown")
                        with tags.button(type="button", cls="btn btn-primary") as b:
                            tags.attr(href="#") #, cls="dropdown-toggle")
                            with tags.span():
                                tags.attr(cls="glyphicon glyphicon-menu-hamburger")
                                # b['data-toggle'] = "dropdown"
                        with tags.ul():
                            tags.attr(cls="dropdown-menu dropdown-menu-left scrollable-menu")





    return html_doc


def clean_name(s):
    s = re.sub(u"־", " ", s, flags=re.UNICODE)
    return re.sub(r"[^\w ]", "", s, flags=re.UNICODE)


def close_html_doc(html_doc):
    with html_doc.body.children[-1]:
        assert html_doc.body.children[-1]['class'] == 'container-fluid'
        with tags.div(id="search_modal"):
            tags.attr(cls="modal fade")


    with html_doc:
        # add footnotes content of this section:
        with tags.ol(id="footnotes"):
            for (id) in html_doc.footnote_ids_of_this_html_doc:
                footnote = word_doc_footnotes.footnotes_part.notes[id + 1]
                assert footnote.id == id
                add_footnote_to_output(footnote.paragraphs)

        # add placeholder for searching
        tags.comment("search_placeholder")

    place_holder = "<!--search_placeholder-->"
    with open("input_web/stub_search.html", 'r') as file:
        search_html = file.read()

    html_doc_name = html_doc.index
    name = "debug_%s.html" % html_doc_name
    with open("output/" + name, 'w') as f:
        f.write(html_doc.render(inline=False).encode('utf8'))
    replace_in_file("output/" + name, place_holder, search_html)

    name = "%s.html" % html_doc_name
    with open("output/" + name, 'w') as f:
        f.write(html_doc.render(inline=True).encode('utf8'))
        print "Created ", name
    replace_in_file("output/" + name, place_holder, search_html)


heading_back_to_back = False
pattern = re.compile(r"\W", re.UNICODE)

# returns:
#  None - if no need for new html_doc
#  string - with name of new required html_doc
#  ('UPDATE_NAME', string) - to replace the name of newly opend html_doc
#  ('NEW_LETTER', string) - if needs a new html_doc, but w/o putting it in the main TOC
def is_need_new_html_doc(para):
    global heading_back_to_back
    for (type, text) in para:
        if type in ("heading_title", "heading_section"):
            if not heading_back_to_back:
                heading_back_to_back = True
                return text.strip()
            else:
                # the previous, and this, are headings - unite them
                if html_docs_l[-1].name != u"מדורים":
                    result = html_docs_l[-1].name + " " + text.strip()
                else:
                    # in the special case of 'Section' heading - we don't need it
                    result = text.strip()
                return ('UPDATE_NAME', result)
        elif type == "heading_letter":
            return ('NEW_LETTER', text.strip())

    # if we're here - we didn't 'return text' with a heading
    heading_back_to_back = False

def fix_html_doc_name(name):
    if name == u"מילון הראיה":
        return u"ערכים כלליים"
    else:
        return name

html_docs_l = []
def get_active_html_doc(para):
    name = is_need_new_html_doc(para)
    if name:
        if isinstance(name, tuple):
            op, new = name
            if op == 'NEW_LETTER':
                html_docs_l.append(open_html_doc(op, letter=new))
            else:
                assert op == 'UPDATE_NAME'
                print "Updating ", new
                html_docs_l[-1].name = new
                html_docs_l[-1].section = new
        else:
            fixed_name = fix_html_doc_name(name)
            html_docs_l.append(open_html_doc(fixed_name))
    return html_docs_l[-1]


def open_latex():
    pass
    # nothing to do here...



def latex_type(type):
    if type == "subject_normal":
        return u"ערך"
    elif type in ("sub-subject_normal", "subject_small", "fake_subject_small", "fake_sub-subject_normal"):
        return u"משנה"
    elif type in ("definition_normal", "fake_subject_small_normal"):
        return u"הגדרה"
    elif type == "source_normal":
        return u"מקור"
    elif type == "sub-subject_small":
        return u"צמשנה"
    elif type == "definition_small":
        return u"צהגדרה"
    elif type == "source_small":
        return u"צמקור"
    elif type == "footnote":
        return "footnote"    #TODO: improve footnote
    elif type == "s02Symbol":
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


        elif type == "new_line":
            latex_new_lines_in_raw += 1
            if latex_new_lines_in_raw == 1:
                if data:
                    data += ("\\\\")
            elif latex_new_lines_in_raw == 2:
                data += ("\n\n")
            else:
                pass

        elif type == "footnote":
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

        if type != "new_line":
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


open_latex()
# Here starts the action!
with open('output/debug.txt', 'w') as debug_file:
    for (paragraph, footnote_paragraph) in zip(word_doc.paragraphs, word_doc_footnotes.paragraphs):
        if paragraph.text.strip():
            # print "Paragraph:", paragraph.text, "$"
            para = []
            debug_file.write("\n\nNEW_PARA:\n------\n")
            for (run, footnote_run) in zip(paragraph.runs, footnote_paragraph.runs):
                s = "!%s.%s:%s$" % (run.style.style_id, docxCode2segType.get(run_style_id(run), run_style_id(run)), run.text)
                # print "!%s:%s$" % (docxCode2segType.get(run.style.style_id, run.style.style_id), run.text)
                debug_file.write(s.encode('utf8') + ' ')
                type = docxCode2segType.get(run_style_id(run), "unknown")

                if run.font.size and run.text.strip():
                    size_kind = sizes.match(run.font.size)
                    if size_kind == 'unknown':
                        print "!%s. Size: %d, Bool: %s, %s:%s$" % (size_kind, run.font.size, run.bold, type, run.text)
                    if size_kind not in ('normal', 'unknown'):
                        type = size_kind

                if 'unknown' in type and run.text.strip():
                    type = fix_unknown(run)

                elif type == "DefaultParagraphFont":
                    type = fix_DefaultParagraphFont(run)
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
                        type = fix_sz_cs(run, type)

                    if run.element.rPr.bCs is not None and run.text.strip():
                        type = fix_b_cs(run, type)

                    # NOTE: this footnote number need no fix.
                    # it is a recurrance, therefore it has no id.
                    if is_footnote_recurrence(run, type):
                        type = TS.footnoteRecc
            
                except:
                    pass


                para.append((type, run.text))

                if type == "unknown":
                    if run_style_id(run) not in unknown_list:
                        unknown_list.append(run_style_id(run))
                        print paragraph.text
                        s = "\nMissing: !%s:%s$\n\n" % (run_style_id(run), run.text)
                        print s
                        debug_file.write(s.encode('utf8') + ' ')


                try:
                    # if run.footnote_references:
                    footnote_references = footnote_run.footnote_references
                    if footnote_references:
                        for (note) in footnote_references:
                            if create_html:
                                html_doc.footnote_ids_of_this_html_doc.append(note.id)
                                relative_note_id = note.id - html_doc.footnote_ids_of_this_html_doc[0] + 1
                                # print "footnote", relative_note_id
                                para.append((TS.footnote, str(relative_note_id)))
                            elif create_latex:
                                #TODO:  we have a problem here!
                                #what happens in case of both html & latex??
                                para.append((TS.footnote, str(note.id)))

                except:
                    print "Failed footnote_references"


            para.append(("new_line", "\n"))
            para = analyze_and_fix(para)
            if create_html:
                html_doc = get_active_html_doc(para)
                add_to_output(html_doc, para)
            if create_latex:
                add_to_latex(para)
        else:
            try:
                # if there is a 'html_doc' - add to id new_line for the paragraph ended
                # if there isn't - it doesn't matter, we're just at the beginning - ignore it
                para = []
                para.append(("new_line", "\n"))
                if create_html:
                    html_doc = html_docs_l[-1]
                    add_to_output(html_doc, para)
                if create_latex:
                    add_to_latex(para)
            except:
                pass

def replace_in_file(file_name, orig_str, new_str):
    with open(file_name, 'r') as file:
        filedata = file.read()

    filedata = filedata.replace(orig_str, new_str)

    with open(file_name, 'w') as file:
        file.write(filedata)


def add_menu_to_apriory_htmls(html_docs_l):
    # add menus to index.html and search.html
    menu_bar = copy.deepcopy(html_docs_l[0].body.children[0].children[1])
    assert menu_bar['id'] == 'menu_bar'
    content = menu_bar.children[0].children[-1].children[1].children
    del(content[6].attributes['class'])

    place_holder = "<!--menu_bar-->"

    menu_bar_html = menu_bar.render(inline=True).encode('utf8')

    with open("input_web/stub_search.html", 'r') as file:
        menu_bar_html += file.read()

    replace_in_file('output/search.html', place_holder, menu_bar_html)

    for index, filename in enumerate((
            'index.html',
            "opening_intros.html",
            "opening_haskamot.html",
            "opening_abbrev.html",
            "opening_signs.html",
    )):
        content[index].attributes['class'] = 'active'
        menu_bar_html = menu_bar.render(inline=True).encode('utf8')
        with open("input_web/stub_search.html", 'r') as file:
            menu_bar_html += file.read()

        replace_in_file('output/%s' % filename, place_holder, menu_bar_html)
        del content[index].attributes['class']


if create_html:
    html_docs_l = fix_links(html_docs_l)
    add_menu_to_apriory_htmls(html_docs_l)

    for (html_doc) in html_docs_l:
        close_html_doc(html_doc)

if create_latex:
    close_latex()

with open('output/subjects_db.json', 'wb') as fp:
    s = json.dumps(subjects_db, encoding='utf8')
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