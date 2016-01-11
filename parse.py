# -*- coding: utf-8 -*-

# do something with new-lines?
#TODO: zip index,css,config.xml
#TODO: remove out 'styles' dict
#TODO: handle footnotes
#TODO: TOC

#TODO: icon
#TODO: automate build
#TODO: iphone?



# from docx import Document
import docx
import docx_fork_ludoo
import dominate
from dominate.tags import *
import sys
#
# import docx2txt
# text = docx2txt.process("snippet2.docx")
# print text

doc_file_name = 'dict.docx'
# doc_file_name = 'snippet1.docx'
#doc_file_name = 'snippet2.docx'

# word_doc = docx.Document(doc_file_name)
# word_doc_footnotes = docx_fork_ludoo.Document(doc_file_name)

#word_doc = docx.Document(doc_file_name)
word_doc =  docx_fork_ludoo.Document(doc_file_name)


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

#
# for (i, para) in enumerate(word_doc.paragraphs):
#     old_para = word_doc_footnotes.paragraphs[i]
#     for (j, run) in enumerate(para.runs):
#         old_run = old_para.runs[j]
#         if run.text.split() != old_run.text.split():
#             print "!! DIFF text!!"
#             print "new:", run.text,"!"
#             print "old:", old_run.text,"!"
#         if run_style_id(run) != run_style_id(old_run) and run_style_id(run) != "DefaultParagraphFont":
#             print "!! DIFF style!!"
#             print "new:", run_style_id(run),"!"
#             print "old:", run_style_id(old_run),"!"
#
#     # if para.text != word_doc_footnotes.paragraphs[i].text:
#     #     print "!! DIFF !!"
#     #     print "new:", para.text,"!"
#     #     print "old:", word_doc_footnotes.paragraphs[i].text,"!"

# print "passed sanity check"

# xml = word_doc.part.blob
# print xml


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

# def add_to_output(type, orig_text):
#     text = orig_text   # .strip()
#     if text != "" and text != "\n":
#         if type == 'subject':
#             p()
#             # a(name=text)
#             with span(a(text, href="#%s" % text, id=text)):
#                 attr(cls=type)
#         else:
#             with span(text):
#                 attr(cls=type)

def subject(text):
    type = 'subject'
    with span(a(text, href="#%s" % text, id=text)):
        attr(cls=type)

def regular(type, text):
    with span(text):
        attr(cls=type)

# by default, check if 'para[i]' is 'subject'
# if Next=True --> check if next index is 'subject', bypassing all 'empty' values
def is_subject(para, i, next=False):
    # try:
    #     continue_loop = True
    #     while continue_loop:
    #         type, text = para[i]
    #         continue_loop = next and text.strip() == ""
    #         i += 1
    #     print "is? ", type, text.strip()
    #     return type == 'subject'
    # except:
    #     print "is? out of index"
    #     return False

    type, text = para[i]
    # print "is? ", type, text.strip()
    return 'subject' in type


def analyze(para):
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

    # fix
    return new_para

def is_prev_subject(para, i):
    try:
        return is_subject(para, i-2) and para[i-1][1].strip() == "-"
    except:
        return False

def add_to_output(para):
    # we shouldn't accept empty paragraph (?)
    assert len(para) > 0

    # if there is only 1 'subject' item in the paragraph, it's probably a heading
    first_type, first_text = para[0]
    if len(para) == 1 and first_type == 'subject':
        # take the 'text' of the first item
        h3(first_text)
    else:
        for (i, (type, text)) in enumerate(para):
            if is_subject(para, i):
                if not is_prev_subject(para, i):
                    p()
                subject(text)
            else:
                regular(type, text)
        # if is_subject(para, i, next=True):
        #     p()
        p()

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

html_doc = dominate.document(title=u"מילון הראיה")
html_doc['dir'] = 'rtl'
with html_doc.head:
    link(rel='stylesheet', href='style.css')

with open('debug.txt', 'w') as debug_file:
    with html_doc:
        for (paragraph) in word_doc.paragraphs:
            if paragraph.text.strip():
                # print "Paragraph:", paragraph.text, "$"
                para = []
                debug_file.write("\n\nNEW_PARA:\n------\n")
                for (run) in paragraph.runs:
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

                para = analyze(para)
                add_to_output(para)


        # for footnote in word_doc_footnotes.footnotes_part.notes:
        #     print footnote



if unknown_list:
    print "\n\nMissing:"
    print unknown_list

with open('debug.html', 'w') as debug_file:
    debug_file.write(html_doc.render(inline=False).encode('utf8'))
    print "Created debug.html"

with open('index.html', 'w') as debug_file:
    debug_file.write(html_doc.render(inline=True).encode('utf8'))
    print "Created index.html"
