# -*- coding: utf-8 -*-

# hopefully, some day, this file will contain much more of tex-related code

import os
import subprocess
import codecs
import footer
import re

sections_csv_file = "sections_short_names.csv"


def reverse_words(s):
    w1 = s.split()
    w2 = reversed(w1)
    return ' '.join(w2)

# the output is 'reversed' due to some bug in 'fancytabs' that shows the words reversed in the string
# TODO: report this bug...
def get_section_short_name(section):
    # I'd prefer to use 'csv' package, but it doesn't behave well with Unicode...
    # with open(sections_csv_file, 'r') as csvfile:

    # the "-sig" is required to ignore BOM (=some sort of Unicode white space)
    csvfile = codecs.open(sections_csv_file, encoding='utf-8-sig')
    for row in csvfile:
        s = row.strip().split(',')
        if s[0].replace('"','') == section.replace('"',''):
            return reverse_words(s[1])
    print "CSV failed search for: ", section
    return reverse_words(section)




def open_latex():
    pass
    # nothing to do here...



def latex_type(type):
    if type in ("subject_normal", "fake_subject_normal"):
        return u"ערך"
    elif type in ("sub-subject_normal", "subject_small", "fake_subject_small", "fake_sub-subject_normal"):
        return u"משנה"
    elif type in ("definition_normal", "fake_subject_small_normal"):
        return u"הגדרה"
    elif type == "source_normal":
        return u"מקור"
    elif type == "sub-subject_small":
        return u"צמשנה"
    elif type == "fake_sub-subject_small":
        return u"צהגדרהמודגשת"
    elif type == "definition_small":
        return u"צהגדרה"
    elif type == "source_small":
        return u"צמקור"
    elif type == "subject_light":
        return u"תערך"
    elif type == "sub-subject_light":
        return u"תמשנה"
    elif type in ("definition_light", "unknown_light"):
        return u"תהגדרה"
    elif type == "source_light":
        return u"תמקור"
    elif type == "s02Symbol":
        return u"מעוין"
    #elif type == "DefaultParagraphFont":
    #    return #TODO: what??
    else:
        # print "TAKALA: ", type
        return u"תקלה"

prev_line = ""
def add_line_to_data(data, line):
    global prev_line
    global latex_data
    if line.startswith("\\my") and prev_line.startswith("\\my") and line.split('{')[0] == prev_line.split('{')[0]:
        # this matches things of either kind:
        # \mychapter{a}{b}    # .group(1) = 'chapter'      , .group(2) = 'a', group(3) = '{b}', group(4) = 'b'
        # \mysubsection{a}    # .group(1) = 'mysubsection' , .group(2) = 'a', group(3) is None, group(4) is None
        r = re.compile(r"\\my(\w+)\{([^{}]+)\}({([^{}]+)\})?", re.UNICODE)
        r_line = r.match(line)
        r_prev_line = r.match(prev_line)
        if r_line.group(1) == r_prev_line.group(1) and r_prev_line.group(2) != u'מדורים':
            # we need to unite prev_line and line

            # remove 'prev_line'
            latex_data = latex_data.replace(prev_line, "")
            data = data.replace(prev_line, "")

            # create united line
            name = r_prev_line.group(2) + ' \protect\\\\ ' + r_line.group(2)
            simple_name = r_prev_line.group(2) + ' ' + r_line.group(2)
            line = u"\\my%s{%s}{%s}" % (r_line.group(1), name, get_section_short_name(simple_name))

    data += line
    prev_line = line
    return data


latex_data = ""
latex_new_lines_in_raw = 0
num_of_heading_titles = 0


next_define_is_moto = False
next_define_ends_moto = False
def set_moto(text):
    global next_define_is_moto
    if u"פסוקים" in text:
        next_define_is_moto = True


def begin_moto():
    return """
    \\end{multicols}
    \\thispagestyle{empty}
    \\vspace*{0.2cm}
    \\begin{adjustbox}{minipage=8cm,margin=0pt \smallskipamount,center}
"""


def end_moto():
    return """
    \\end{adjustbox} 
    \\clearpage
    \\begin{multicols}{2}
    """

def add_to_latex(para, word_doc_footnotes):
    global latex_new_lines_in_raw
    global latex_data
    global num_of_heading_titles

    data = ""
    for (i, (type, text)) in enumerate(para):
        data = handle_moto(data, text, type)

        if 'heading' in type and text.strip():

            # TODO: adjust headings
            if type == 'heading_title':
                data = add_line_to_data(data, "\\mychapter{%s}{%s}" % (text, get_section_short_name(text)))
                num_of_heading_titles += 1
            elif type == 'heading_section':
                set_moto(text)
                if next_define_is_moto:
                    chapter_command = "mymotochapter"
                else:
                    chapter_command = "mychapter"
                data = add_line_to_data(data, "\\%s{%s}{%s}" % (chapter_command, text, get_section_short_name(text)))
            elif type == 'heading_sub-section-bigger':
                data = add_line_to_data(data, "\\mysubsection{%s}" % (text))
            elif type == 'heading_sub-section':
                data = add_line_to_data(data, "\\mysubsection{%s}" % (text))
            elif type == 'heading_letter':
                if num_of_heading_titles >= 2:
                    data = add_line_to_data(data, "\\myletterslave{%s}" % (text))
                else:
                    data = add_line_to_data(data, "\\mylettertitle{%s}" % (text))
            data += "\n"



        elif type == "new_line":
            latex_new_lines_in_raw += 1
            if latex_new_lines_in_raw == 1:
                if data:
                    data += ("\\\\")
            elif latex_new_lines_in_raw == 2:
                # chop the "new line" symbol - not required before new paragraph
                assert latex_data[-2:] == "\\\\" or data[-2:] == "\\\\"
                if data[-2:] == "\\\\":
                    data = data[:-2]
                elif latex_data[-2:] == "\\\\":
                    latex_data = latex_data[:-2]
                data += ("\n\n")
            else:
                pass

        elif type == "footnote":
            id = int(text)
            footnote = word_doc_footnotes.footnotes_part.notes[id + 1]
            assert footnote.id == id

            all_runs_list = []
            for (para) in footnote.paragraphs:
                foot_text = ""
                for (run) in para.runs:
                    style = footer.get_style(run)
                    if style == "bolded":
                        foot_text += (("\\%s{%s}" % ("textbf", run.text)))
                    else:
                        foot_text += (run.text)
                all_runs_list.append(foot_text)

            all_runs_text = "\\newline\n".join(all_runs_list)
            data = add_line_to_data(data, "\\%s{%s\label{%s}}" % ("myfootnote", all_runs_text, id))

        elif type == "footnote_recurrence":
            data = add_line_to_data(data, "\\%s{%s} " % ('footref', text.strip()))


        # elif is_subject(para, i):
        #     if not is_prev_subject(para, i):
        #         # tags.p()
        #         #tags.br()
        #         pass
        #     subject(html_doc, type, text)
        else:
            # regular(type, text)
            data = add_line_to_data(data, "\\%s{%s}" % (latex_type(type), text))


        if type != "new_line":
            latex_new_lines_in_raw = 0

    latex_data += data


def handle_moto(data, text, type):
    global next_define_is_moto, next_define_ends_moto
    if latex_type(type) == u"ערך" and next_define_is_moto:
        data += begin_moto()
        next_define_is_moto = False
        next_define_ends_moto = True
    elif (('heading' in type and text.strip()) or latex_type(type) == u"ערך") and next_define_ends_moto:
        data += end_moto()
        next_define_is_moto = False
        next_define_ends_moto = False
    return data


def run_xelatex(f):
    try:
        subprocess.call(['xelatex', f])
    except:
        subprocess.call([r'C:\Users\zharamax\AppData\Local\Programs\MiKTeX 2.9\miktex\bin\x64\xelatex', f])


def close_latex():
    global latex_data
    latex_data = latex_data.replace('"',u"״")
    latex_data = latex_data.replace("'",u"׳")

    os.chdir("tex")

    with open("content.tex", 'a') as latex_file:
        latex_file.write(latex_data.encode('utf8'))


    # twice because of thumb-indices
    run_xelatex('milon.tex')
    run_xelatex('milon.tex')
    os.startfile("milon.pdf")
    os.chdir("..")

