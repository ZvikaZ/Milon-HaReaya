# -*- coding: utf-8 -*-
""" Currently, this is the 'main' module of this project.
By default, it parses 'dict.docx' (that contains Milon HaReaya's source Word file,
creates 'html_docs_l' - internal representation of all the Milon,
'subjects_db' which is used for searching (and is written as JSON file for the JS)
and then creates 'output/' with a working HTML/CSS/JS site, and zips it to 'milon.zip'

If 'secret.py' exists, it then uploads the .zip file to PhoneGap Build, waits for the .apk
to be ready, downloads it (to output/) and pushes everything (automatically) to Google Play.
"""

# TODO: double footnote, like #8 - recognize also the second
# TODO: Yud and Lamed in Psukim
# TODO: "Mehkarim" - make links, check styles!
# TODO: Add "Ptiha"
# TODO: handle footnotes' styles
# TODO: "Ayen", "Re'e" - see mail from 22.1.16
# TODO: "all subjects" page

# TODO: splitted bubject, like "אמר לו הקדוש ברוך הוא (לגבריאל° שבקש להציל את אברהם־אבינו° מכבשן האש) אני יחיד בעולמי והוא יחיד בעולמו, נאה ליחיד להציל את היחיד"
# TODO: make headings to links
# TODO: save current location (and history?, with back and forward?) - use HTML5 local storage
# TODO: search - better results page
# TODO: circles support multi definitions
# TODO: MENU: add current section, about
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

import build_phonegap
import upload_google_play


html_parser = HTMLParser.HTMLParser()

process = "Full"
#process = "APK"
#process = "ZIP"

if process == "Full":
    doc_file_name = 'dict.docx'
else:
    #doc_file_name = 'dict_few.docx'
    #doc_file_name = 'dict_check.docx'
    #doc_file_name = 'dict_short.docx'
    doc_file_name = 'dict.docx'


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


styles = {
    's01': 'subject_normal',
    's11': 'sub-subject_normal',
    's02': 'definition_normal',
    's03': 'source_normal',
    'Heading3Char': 'definition_normal',
    '1': 'definition_normal',   #?
    'FootnoteTextChar1': 'definition_normal',   #?
    'HebrewChar': 'definition_normal',   #?

    # this is problematic! has its own function to handle it
    'DefaultParagraphFont': 'DefaultParagraphFont',

    's15': 'subject_small',
    's17': 'subject_small',
    's1510': 'subject_small',
    's05': 'definition_small',
    's038': 'source_small',
    's0590': 'source_small',
    's050': 'source_small',
    '050': 'source_small',

    's149': 'subject_light',
    's16': 'subject_light',
    's14': 'subject_light',
    's168': 'sub-subject_light',
    's048': 'definition_light',
    's12': 'definition_light',
    's04': 'unknown_light',
    's127': 'source_light',

    's02Symbol': 's02Symbol',   # MeUyan

    'FootnoteReference': 'FootnoteReference',
    'EndnoteReference': 'EndnoteReference', #?
}

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

def calc_subject_id(text, cnt):
    # subject_id = "subject_%d" % len(subjects_db)
    # subject_id = text.strip()
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
    if type == 'footnote':
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
        return is_subject(para, i-2) and para[i-1][1].strip() == "-"
    except:
        return False

def is_prev_newline(para, i):
    try:
        return para[i-2][0] == "new_line" and para[i-1][1] == ""
    except:
        return False

def make_sub_subject(subj):
    if subj == 'subject_small':
        return 'sub-subject_normal'
    else:
        return subj

def analyze_and_fix(para):
    # unite splitted adjacent similar types
    prev_type, prev_text = None, ""
    new_para = []
    for (type, text_raw) in para:
        text = text_raw.replace("@", "")
        if prev_type:
            if type == prev_type or text.strip() in ("", u"°", u"־", ","):
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
            if (index == 0) or (is_prev_newline(para, index)):
                new_para.append((type, text))
            elif (is_prev_subject(para, index)):
                new_para.append((make_sub_subject(type), text))
            elif new_para[index-1][0] in ('sub-subject_normal', 'subject_small'):
                new_para.append((make_sub_subject(type), text))
            else:
                new_para.append(("fake_"+type, text))

        else:
            new_para.append((type, text))

    # fix wrong 'source's
    para = new_para
    new_para = []
    source_pattern = re.compile(r"(\[.*\])")
    for (type, text) in para:
        if type == 'source_normal':
            small = False
            for (chunk) in source_pattern.split(text):
                if source_pattern.match(chunk):
                    if small:
                        new_para.append(('source_small', chunk))
                    else:
                        new_para.append((type, chunk))
                elif chunk.strip() != "":
                    new_para.append(('definition_small', chunk))
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
            debug_file.write(s.encode('utf8'))

    # fix
    return new_para

# return True if updated
def update_values_for_href(child, href):
    values = subjects_db.get(href)
    #TODO: support showing more than 1 result
    if values:
        _, _, url = values[0]
        child.children[0]['href'] = url
        return True

def update_href_no_link(child):
    assert len(child.children[0].children) == 1
    text = html_parser.unescape(child.children[0].children[0])
    child.children[0] = tags.span(text)

def fix_links(html_docs_l):
    # fix outbound links
    print "Fixing links"
    for (doc) in html_docs_l:
        for (child) in doc.body.children:
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

                    except:
                        pass
                        #TODO - investigate why it happens? (it's a single corner case, I think)



    # update sections menu
    for (doc) in html_docs_l:
        letters_l = []
        fixbar = doc.head.children[-1]
        assert fixbar['class'] == 'fixbar'
        dropdown = fixbar.children[0].children[-1]  # fixbar.children[0]
        assert dropdown['class'] == 'dropdown'
        dropdown_content = dropdown.children[-1]
        assert dropdown_content['class'] == 'dropdown-content'
        with dropdown_content:
            for (html_doc) in html_docs_l:
                # Only if this a 'high' heading, and not just a letter - include it in the TOC
                if html_doc.name != "NEW_LETTER":
                    if doc.section != html_doc.section:
                        tags.a(html_doc.name, href=str(html_doc.index)+".html")
                    else:
                        tags.strong(html_doc.name)
                else:
                    # it's a letter - if it's related to me, save it
                    if doc.section == html_doc.section:
                        letters_l.append(html_doc)

        with doc.body:
            with tags.ul():
                tags.attr(cls="letters_navbar")
                for (html_doc) in letters_l:
                    with tags.li(tags.a(html_doc.letter, href=str(html_doc.index)+".html")):
                        tags.attr(cls="letters_links")



    return html_docs_l

new_lines_in_raw = 0
def add_to_output(html_doc, para):
    global new_lines_in_raw
    # we shouldn't accept empty paragraph (?)
    assert len(para) > 0

    with html_doc:
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
            debug_file.write(s.encode('utf8'))
            return 'subject_small'
    elif szCs == "22" and type == 'definition_normal':
        return 'subject_normal'
    elif szCs == "16" and type == 'source_normal':
        return 'source_small'
    else:
        pass
    return result

def fix_b_cs(run, type):
    result = type
    try:
        bCs = run.element.rPr.bCs.attrib.values()[0]
        if bCs == "0" and 'subject' in type:
            if type in ('subject_small', 'sub-subject_normal'):
                return 'definition_normal'
            else:
                pass
                # print "Unknown b_cs=0"
    except:
        pass
    return result

def fix_unknown(run):
    if run.font.size == 114300 and run.style.style_id == 's04':
        return 'subject_light'
    elif run.font.size == 101600 and run.style.style_id == 's04' and run.font.cs_bold:
        return 'sub-subject_light'
    elif run.font.size == 101600 and run.style.style_id == 's04' and not run.font.cs_bold:
        return 'definition_light'
    elif run.font.size is None and run.style.style_id == 's04':
        return 'definition_light'
    elif run.font.size == 88900 and run.style.style_id == 's04':
        return 'source_light'
    else:
        return 'unknown_light'


def fix_DefaultParagraphFont(run):
    # only if it's really a text
    if run.text.strip() and run.text.strip() not in ("-", "(", ")", "[", "]", "'", '"', ","):
        if run.font.size == 152400 and not run.bold:
            return 'subject_normal'
        if run.font.size == 139700 and run.bold:
            return 'subject_normal'
        elif run.font.size == 127000:
            return 'definition_normal'
        elif run.font.size == 114300:
            return 'source_normal'
        elif run.font.size == 101600:
            return 'source_small'
        elif run.font.size == 88900:
            return 'source_small'
        elif run.font.size is None and run.bold:
            return 'sub-subject_normal'
        elif run.font.size is None and not run.bold:
            return 'definition_normal'
        else:
            print "AH!", ":",run.text.strip(),".", run.font.size, run.bold
            assert False
    else:
        return 'DefaultParagraphFont'

temp_l = []
def bold_type(s, type, run):
    if type == 'definition_normal':
        return 'subject_small'
    elif type == 'source_normal' and run.style.style_id == "s03":
        return 'sub-subject_small'
    elif type == "definition_small" and run.style.style_id == "s05":
        return 'sub-subject_small'
    elif type == 'source_normal' and run.style.style_id == "DefaultParagraphFont" and run.font.size == 139700:
        return 'subject_normal'
    elif type == 'source_normal' and run.style.style_id == "DefaultParagraphFont" and run.font.size != 139700:
        return 'sub-subject_normal'
    elif type == 'unknown_light' and run.style.style_id == "s04" and run.font.size == 114300:
        return 'subject_light'
    elif type == 'unknown_light' and run.style.style_id == "s04" and run.font.size == 101600:
        return 'sub-subject_light'
    elif type == 'definition_light' and run.style.style_id == "s12" and run.font.size == 101600:
        return 'sub-subject_light'
    elif type == 'definition_light' and run.style.style_id == "s12" and run.font.size is None:
        # TODO - verify that it's always OK
        return 'sub-subject_light'
    elif type == 'source_normal':
        print "Strange 'source_normal' bold!"
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
        tags.link(rel='stylesheet', href='style.css')
        tags.link(rel='stylesheet', href='fixed_bar.css')
        tags.link(rel='stylesheet', href='html_demos-gh-pages/footnotes.css')
        tags.script(src="html_demos-gh-pages/footnotes.js")
        tags.script(src="milon.js")
        tags.script(src="subjects_db.json")

        #TODO: MENU: TOC, search, current section, about
        with tags.div():
            tags.attr(cls="fixbar")
            with tags.ul():
                tags.input(type="search", id="subject_search", placeholder = (u"ערך לחיפוש"), onchange='search()')

                with tags.div():
                    tags.attr(cls="dropdown")
                    with tags.button(u"תוכן"):
                        tags.attr(cls="dropbtn")
                    with tags.div():
                        tags.attr(cls="dropdown-content")


    html_doc.footnote_ids_of_this_html_doc = []
    html_doc.name = name
    if letter:
        html_doc.letter = letter
        html_doc.section = html_docs_l[-1].section
    else:
        html_doc.section = name

    html_doc.index = len(html_docs_l) + 1
    with html_doc.body:
        # TODO: call page_loaded to update saved URL also in other links
        tags.script("page_loaded('%s.html')" % html_doc.index)


    return html_doc


def clean_name(s):
    s = re.sub(u"־", " ", s, flags=re.UNICODE)
    return re.sub(r"[^\w ]", "", s, flags=re.UNICODE)


def close_html_doc(html_doc):
    with html_doc:
        # add footnotes content of this section:
        with tags.ol(id="footnotes"):
            for (id) in html_doc.footnote_ids_of_this_html_doc:
                footnote = word_doc_footnotes.footnotes_part.notes[id + 1]
                assert footnote.id == id
                add_footnote_to_output(footnote.paragraphs)

    html_doc_name = html_doc.index
    name = "debug_%s.html" % html_doc_name
    with open("output/" + name, 'w') as f:
        f.write(html_doc.render(inline=False).encode('utf8'))

    name = "%s.html" % html_doc_name
    with open("output/" + name, 'w') as f:
        f.write(html_doc.render(inline=True).encode('utf8'))
        print "Created ", name

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
        else:
            html_docs_l.append(open_html_doc(name))
    return html_docs_l[-1]


try:
    shutil.rmtree("output")
except:
    pass

os.mkdir("output")
os.mkdir("output/html_demos-gh-pages")
for (f) in (
    'config.xml',
    'icon.png',
    'style.css',
    'fixed_bar.css',
    'html_demos-gh-pages/footnotes.css',
    'html_demos-gh-pages/footnotes.js',
    'milon.js',
    'index.html',
    'search.html',
):
    shutil.copyfile(f, os.path.join("output", f))

# Here starts the action!
with open('output/debug.txt', 'w') as debug_file:
    for (paragraph, footnote_paragraph) in zip(word_doc.paragraphs, word_doc_footnotes.paragraphs):
        if paragraph.text.strip():
            # print "Paragraph:", paragraph.text, "$"
            para = []
            debug_file.write("\n\nNEW_PARA:\n------\n")
            for (run, footnote_run) in zip(paragraph.runs, footnote_paragraph.runs):
                s = "!%s.%s:%s$" % (run.style.style_id, styles.get(run_style_id(run), run_style_id(run)), run.text)
                # print "!%s:%s$" % (styles.get(run.style.style_id, run.style.style_id), run.text)
                debug_file.write(s.encode('utf8'))
                type = styles.get(run_style_id(run), "unknown")

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

                try:
                    if run.element.rPr.szCs is not None and run.text.strip():
                        type = fix_sz_cs(run, type)

                    if run.element.rPr.bCs is not None and run.text.strip():
                        type = fix_b_cs(run, type)
                except:
                    pass


                para.append((type, run.text))

                if type == "unknown":
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
                            html_doc.footnote_ids_of_this_html_doc.append(note.id)
                            relative_note_id = note.id - html_doc.footnote_ids_of_this_html_doc[0] + 1
                            para.append(('footnote', str(relative_note_id)))
                except:
                    print "Failed footnote_references"


            para.append(("new_line", "\n"))
            para = analyze_and_fix(para)
            html_doc = get_active_html_doc(para)
            add_to_output(html_doc, para)
        else:
            try:
                # if there is a 'html_doc' - add to id new_line for the paragraph ended
                # if there isn't - it doesn't matter, we're just at the beginning - ignore it
                para = []
                para.append(("new_line", "\n"))
                html_doc = html_docs_l[-1]
                add_to_output(html_doc, para)
            except:
                pass

html_docs_l = fix_links(html_docs_l)

for (html_doc) in html_docs_l:
    close_html_doc(html_doc)

with open('output/subjects_db.json', 'wb') as fp:
    s = json.dumps(subjects_db, encoding='utf8')
    fp.write("data = " + s)


if unknown_list:
    print "\n\nMissing:"
    print unknown_list


with zipfile.ZipFile("milon.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    for dirname, subdirs, files in os.walk("output"):
        zf.write(dirname)
        for filename in files:
            if not 'debug' in filename:
                zf.write(os.path.join(dirname, filename))
    print "Created milon.zip"

shutil.move("milon.zip", "output/")

if process != "ZIP":
    try:
        build_phonegap.push_to_phonegap("output/milon.zip")
        if process == "Full":
            upload_google_play.main()
    except Exception as e:
        print "Build process failed!"
        print e