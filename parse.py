# -*- coding: utf-8 -*-

#TODO: zip index,css,config.xml
#TODO: git
#TODO: remove out 'styles' dict
#TODO: handle footnotes
#TODO: TOC

#TODO: icon
#TODO: automate build
#TODO: iphone?



from docx import Document
import dominate
from dominate.tags import *
import sys

word_doc = Document('dict.docx')
#word_doc = Document('snippet1.docx')
#word_doc = Document('snippet2.docx')


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

def add_to_output(type, orig_text):
    text = orig_text   # .strip()
    if text != "" and text != "\n":
        if type == 'subject':
            p()
            # a(name=text)
            with span(a(text, href="#%s" % text, id=text)):
                attr(cls=type)
        else:
            with span(text):
                attr(cls=type)


html_doc = dominate.document(title=u"מילון הראיה")
html_doc['dir'] = 'rtl'
with html_doc.head:
    link(rel='stylesheet', href='style.css')

with open('debug.txt', 'w') as f:
    with html_doc:
        paragraphs = word_doc.paragraphs
        i = 0
        stop_on = -10
        for (paragraph) in paragraphs:
            if paragraph.text.strip():
                # print "Paragraph:", paragraph.text, "$"
                for (run) in paragraph.runs:
                    i += 1
                    # if i == stop_on:
                    #     print "breaking!"
                    #     break
                    s = "!%s:%s$" % (styles.get(run.style.style_id, run.style.style_id), run.text)
                    # print "!%s:%s$" % (styles.get(run.style.style_id, run.style.style_id), run.text)
                    f.write(s.encode('utf8'))
                    type = styles.get(run.style.style_id, "unknown")
                    add_to_output(type, run.text)
                    if type == "unknown":
                        if run.style.style_id not in unknown_list:
                            unknown_list.append(run.style.style_id)
                            print paragraph.text
                            s = "\nMissing: !%s:%s$\n\n" % (run.style.style_id, run.text)
                            print s
                            f.write(s.encode('utf8'))

                    # if run.style.style_id not in styles: # and False:
                    #     print "Missing: !%s:%s$" % (run.style.style_id, run.text),
                    #     stop_on = i + 5
                    #     sys.exit(1)



# print html_doc.render()

print "\n\nMissing:"
print unknown_list

with open('debug.html', 'w') as f:
    f.write(html_doc.render(inline=False).encode('utf8'))
    print "Created debug.html"

with open('index.html', 'w') as f:
    f.write(html_doc.render(inline=True).encode('utf8'))
    print "Created index.html"
