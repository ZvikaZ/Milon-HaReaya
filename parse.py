# -*- coding: utf-8 -*-

#TODO: split into smaller HTML files
#TODO: handle footnotes' styles
#TODO: TOC, search
#TODO: make footnotes to be superscript, without using ()
#TODO: try to decrease footnotes counter
#TODO: make smart links on circles (identify BAKHLAM, etc.)

#TODO: remove out 'styles' dict
#TODO: icon
#TODO: automate build
#TODO: iphone?



import docx
import docx_fork_ludoo
import dominate
import dominate.tags as tags
import re
import zipfile
import os

#doc_file_name = 'dict.docx'
doc_file_name = 'dict_short.docx'
#doc_file_name = 'snippet2.docx'

# word_doc = docx.Document(doc_file_name)
# word_doc_footnotes = docx_fork_ludoo.Document(doc_file_name)

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
    's01': 'subject',
    's11': 'sub-subject',
    's02': 'definition',
    's03': 'source',
    'Heading3Char': 'definition',
    '1': 'definition',   #?
    'FootnoteTextChar1': 'definition',   #?
    'HebrewChar': 'definition',   #?
    'DefaultParagraphFont': 'source',    #?

    's15': 'subject_small',
    's17': 'subject_small',
    's1510': 'unknown_small',
    's05': 'definition_small',
    's038': 'source_small',
    's0590': 'source_small',
    's050': 'source_small',

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

unknown_list = []


def subject(type, text):
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
            if (index == 0) or \
                    (is_prev_newline(para, index)) or (is_prev_subject(para, index)):
                new_para.append((type, text))
            else:
                new_para.append(("fake_"+type, text))

        else:
            new_para.append((type, text))

    # fix wrong 'source's
    para = new_para
    new_para = []
    source_pattern = re.compile(r"(\[.*\])")
    for (type, text) in para:
        if type == 'source':
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



    with open('debug_fix.txt', 'a') as debug_file:
        debug_file.write("---------------\n")
        for (type, text) in new_para:
            s = "%s:%s.\n" % (type, text)
            debug_file.write(s.encode('utf8'))

    # fix
    return new_para


def add_to_output(para):
    # we shouldn't accept empty paragraph (?)
    assert len(para) > 0

    # if there is only 1 'subject' item in the paragraph, it's probably a heading
    first_type, first_text = para[0]
    if len(para) == 1 and first_type == 'subject':
        # take the 'text' of the first item
        tags.h3(first_text)
    else:
        for (i, (type, text)) in enumerate(para):
            if type == "new_line":
                tags.br()
            elif is_subject(para, i):
                if not is_prev_subject(para, i):
                    # tags.p()
                    #tags.br()
                    pass
                subject(type, text)
            else:
                regular(type, text)

        # tags.br()

def add_footnote_to_output(id, paragraphs):
    text = ""
    for (para) in paragraphs:
        text += para.text
    tags.li(text)


temp_l = []
def bold_type(type):
    if type == 'definition':
        return 'subject_small'
    elif type == 'source':
        return 'sub-subject'
    elif 'subject' in type:
        return type
    else:
        if type not in temp_l:
            print "Unexpected bold!", type
            temp_l.append(type)
        return type

try:
    os.remove("debug_fix.txt")
except:
    pass

html_doc = dominate.document(title=u"מילון הראיה")
html_doc['dir'] = 'rtl'
with html_doc.head:
    tags.link(rel='stylesheet', href='style.css')
    tags.link(rel='stylesheet', href='html_demos-gh-pages/footnotes.css')
    tags.script(src="html_demos-gh-pages/footnotes.js")
    tags.script(src="milon.js")
    with tags.div():
        tags.attr(cls="fixbar")
        tags.input(type="search", id="subject_search", onchange='search()')
        tags.button(u"חפש הגדרה", type="button", onclick='search()')

with open('debug.txt', 'w') as debug_file:
    with html_doc:
        for (paragraph, footnote_paragraph) in zip(word_doc.paragraphs, word_doc_footnotes.paragraphs):
            if paragraph.text.strip():
                # print "Paragraph:", paragraph.text, "$"
                para = []
                debug_file.write("\n\nNEW_PARA:\n------\n")
                for (run, footnote_run) in zip(paragraph.runs, footnote_paragraph.runs):
                    s = "!%s:%s$" % (styles.get(run_style_id(run), run_style_id(run)), run.text)
                    # print "!%s:%s$" % (styles.get(run.style.style_id, run.style.style_id), run.text)
                    debug_file.write(s.encode('utf8'))
                    type = styles.get(run_style_id(run), "unknown")
                    if run.bold:
                        type = bold_type(type)
                    # add_to_output(type, run.text)
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
                                para.append(('footnote', str(note.id)))
                    except:
                        print "Failed footnote_references"

                    # para.append(("new_line", "\n"))

                # tags.br()
                para.append(("new_line", "\n"))
                para = analyze_and_fix(para)
                add_to_output(para)
            else:
                # print paragraph
                tags.p()
                # tags.br()
                # tags.hr()

            # para.append(("new_line", "\n"))
            # tags.br()
        # tags.hr()

        try:
            with tags.ol(id="footnotes"):
                for footnote in word_doc_footnotes.footnotes_part.notes:
                    if footnote.id >= 1:
                        add_footnote_to_output(footnote.id, footnote.paragraphs)
        except:
            print "Failed footnotes part"



if unknown_list:
    print "\n\nMissing:"
    print unknown_list

with open('debug.html', 'w') as debug_file:
    debug_file.write(html_doc.render(inline=False).encode('utf8'))
    print "Created debug.html"

with open('index.html', 'w') as debug_file:
    debug_file.write(html_doc.render(inline=True).encode('utf8'))
    print "Created index.html"

with zipfile.ZipFile('milon.zip', 'w', zipfile.ZIP_DEFLATED) as myzip:
    for (filename) in (
        'config.xml',
        'index.html',
        'style.css',
        'html_demos-gh-pages/footnotes.css',
        'html_demos-gh-pages/footnotes.js',
        'milon.js',
    ):
        myzip.write(filename)

    print "Created milon.zip"
