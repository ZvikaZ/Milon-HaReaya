# -*- coding: utf-8 -*-

# hopefully, some day, this file will contain much more of tex-related code

import os
import subprocess


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
def add_to_latex(para, word_doc_footnotes):
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

