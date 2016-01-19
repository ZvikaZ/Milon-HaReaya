# -*- coding: utf-8 -*-

# TODO: search - better results page
# TODO: circles support multi definitions
# TODO: split further the HTMLs?
# TODO: "Mehkarim" - make links
# TODO: make headings to links
# TODO: handle footnotes' styles
# TODO: MENU: add current section, about
# TODO: add letters to TOC
# TODO: make smart links on circles (identify BAKHLAM, 'zohama' with Alef or He, etc.)
# TODO: double footnote, like #8 - recognize also the second
# TODO: splitted bubject, like "אמר לו הקדוש ברוך הוא (לגבריאל° שבקש להציל את אברהם־אבינו° מכבשן האש) אני יחיד בעולמי והוא יחיד בעולמו, נאה ליחיד להציל את היחיד"
# TODO: increase/decrease font size
# TODO: "Avnet" - new paragraph?
# TODO: handle new lines in the beginning
# TODO: make definition in new line? (without ' - ')

# TODO: remove out 'styles' dict
# TODO: icon
# TODO: automate build
# TODO: iphone?


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

#full_process = False
full_process = True

if full_process:
    doc_file_name = 'dict.docx'
else:
    doc_file_name = 'dict_short.docx'


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
    'DefaultParagraphFont': 'source_normal',    #?

    's15': 'subject_small',
    's17': 'subject_small',
    's1510': 'unknown_small',
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
# each pointer is a tuple of html_doc's index and text
subjects_db = {}

def subject(html_doc, type, text):
    clean_text = clean_name(text)
    new_subject_l = subjects_db.get(clean_text, [])
    new_subject_l.append((html_doc.index, text))
    subjects_db[clean_text] = new_subject_l

    with tags.span(tags.a(text, href="#%s" % text.strip(), id=text.strip())):
        tags.attr(cls=type)

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
    for (type, text) in para:
        if prev_type:
            if type == prev_type or text.strip() in ("", u"°"):
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
        if 'subject' in type:
            # real subject is either:
            # first
            # after new_line and empty
            # after subject,"-"
            if (index == 0) or (is_prev_newline(para, index)):
                new_para.append((type, text))
            elif (is_prev_subject(para, index)):
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
        html_doc_index, old_href = values[0]
        s = str(html_doc_index) + ".html" + "#" + old_href
        child.children[0]['href'] = s
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
                            if href[0] in (u"ה", u"ו", u"ש"):
                                updated = update_values_for_href(child, href[1:])
                        if not updated:
                            # failed to update - it's not a real link...
                            update_href_no_link(child)

                    except:
                        pass
                        #TODO - investigate why it happens? (it's a single corner case, I think)



    # update sections menu
    for (doc) in html_docs_l:
        fixbar = doc.head.children[-1]
        assert fixbar['class'] == 'fixbar'
        dropdown = fixbar.children[0].children[-1]  # fixbar.children[0]
        assert dropdown['class'] == 'dropdown'
        dropdown_content = dropdown.children[-1]
        assert dropdown_content['class'] == 'dropdown-content'
        with dropdown_content:
            for (html_doc) in html_docs_l:
                if doc != html_doc:
                    tags.a(html_doc.name, href=str(html_doc.index)+".html")
                else:
                    tags.strong(html_doc.name)
    return html_docs_l

def add_to_output(html_doc, para):
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
                tags.br()
            elif is_subject(para, i):
                if not is_prev_subject(para, i):
                    # tags.p()
                    #tags.br()
                    pass
                subject(html_doc, type, text)
            else:
                regular(type, text)

        # tags.br()

def add_footnote_to_output(paragraphs):
    text = ""
    for (para) in paragraphs:
        text += para.text
    tags.li(text)


temp_l = []
def bold_type(s, type, run):
    if type == 'definition_normal':
        return 'subject_small'
    elif type == 'source_normal' and run.style.style_id == "s03":
        return 'sub-subject_small'
    elif type == 'source_normal' and run.style.style_id == "DefaultParagraphFont" and run.font.size == 139700:
        return 'subject_normal'
    elif type == 'source_normal' and run.style.style_id == "DefaultParagraphFont" and run.font.size != 139700:
        return 'sub-subject_normal'
    elif type == 'source_normal':
        print "Strange 'source_normal' bold!"
    elif 'subject' in type:
        return type
    else:
        if type not in temp_l:
            print "Unexpected bold!", type
            temp_l.append(type)
        return type


def open_html_doc(name):
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
                tags.input(type="search", id="subject_search", onchange='search()')
                tags.button(u"חיפוש", type="button", onclick='search()')
                with tags.div():
                    tags.attr(cls="dropdown")
                    with tags.button(u"תוכן"):
                        tags.attr(cls="dropbtn")
                    with tags.div():
                        tags.attr(cls="dropdown-content")


    html_doc.footnote_ids_of_this_html_doc = []
    html_doc.name = name
    html_doc.index = len(html_docs_l) + 1

    return html_doc


def clean_name(s):
    m = re.search(u"([\w ]*\w+)", s, flags=re.UNICODE)
    return m.group(0)


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

    # if we're here - we didn't 'return text' with a heading
    heading_back_to_back = False

html_docs_l = []
def get_active_html_doc(para):
    name = is_need_new_html_doc(para)
    if name:
        if isinstance(name, tuple):
            op, new = name
            assert op == 'UPDATE_NAME'
            print "Updating ", new
            html_docs_l[-1].name = new
        else:
            html_docs_l.append(open_html_doc(name))
            print "Opening ", name
    return html_docs_l[-1]


try:
    shutil.rmtree("output")
except:
    pass

os.mkdir("output")
os.mkdir("output/html_demos-gh-pages")
for (f) in (
    'config.xml',
    'style.css',
    'fixed_bar.css',
    'html_demos-gh-pages/footnotes.css',
    'html_demos-gh-pages/footnotes.js',
    'milon.js',
    'index.html',
):
    shutil.copyfile(f, os.path.join("output", f))


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

                # if run.style.style_id == "DefaultParagraphFont":
                #     print paragraph.style.style_id, paragraph.style.type, paragraph.style.font.size, run.font.size, s

                if run.bold:
                    type = bold_type(s, type, run)

                if run.font.size and run.text.strip():
                    size_kind = sizes.match(run.font.size)
                    if size_kind == 'unknown':
                        print "!%s. Size: %d, Bool: %s, %s:%s$" % (size_kind, run.font.size, run.bold, type, run.text)
                    if size_kind not in ('normal', 'unknown'):
                        type = size_kind

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

                # para.append(("new_line", "\n"))

            # tags.br()
            para.append(("new_line", "\n"))
            para = analyze_and_fix(para)
            html_doc = get_active_html_doc(para)
            add_to_output(html_doc, para)
        else:
            # html_doc.add(tags.p())
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

if full_process:
    build_phonegap.push_to_phonegap("output/milon.zip")
    upload_google_play.main()