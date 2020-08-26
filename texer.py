# -*- coding: utf-8 -*-

# hopefully, some day, this file will contain much more of tex-related code

import os
import subprocess
import codecs
import footer
import re

sections_csv_file = "sections_info.csv"
current_section = {'section': None, 'moto': False, 'intro': False, 'end_of_intro:type': "", 'end_of_intro:text': ""}


def reverse_words(s):
    w1 = s.split()
    w2 = reversed(w1)
    return ' '.join(w2)



def get_bool_from_csv(cell):
    if cell == "" or cell.lower() == "no":
        return False
    elif cell.lower() == "yes":
        return True
    else:
        print("Illegal value in CSV: ", cell)
        assert False


# the output is 'reversed' due to some bug in 'fancytabs' that shows the words reversed in the string
# TODO: report this bug...
def get_section_short_name(section):
    global current_section

    # I'd prefer to use 'csv' package, but it doesn't behave well with Unicode...
    # with open(sections_csv_file, 'r') as csvfile:

    # the "-sig" is required to ignore BOM (=some sort of Unicode white space)
    csvfile = codecs.open(sections_csv_file, encoding='utf-8-sig')
    for row in csvfile:
        s = row.strip().split(',')
        if s[0].replace('"','').strip() == section.replace('"','').strip():
            current_section['section'] = s[1].strip()
            current_section['moto'] = get_bool_from_csv(s[2])
            current_section['intro'] = get_bool_from_csv(s[3])
            current_section['end_of_intro:type'] = s[4].strip()
            current_section['end_of_intro:text'] = s[5].strip()
            print("CSV found: ", s[1], current_section)
            return reverse_words(current_section['section'])
    print("CSV failed search for: ", section)
    current_section['section'] = section
    current_section['moto'] = False
    current_section['intro'] = False
    current_section['end_of_intro:type'] = ""
    current_section['end_of_intro:text'] = ""
    return reverse_words(current_section['section'])




def open_latex():
    pass
    # nothing to do here...



def latex_type(type):
    if type in ("subject_normal", "fake_subject_normal"):
        return "ערך"
    elif type in ("sub-subject_normal", "subject_small", "fake_subject_small", "fake_sub-subject_normal"):
        return "משנה"
    elif type in ("definition_normal", "fake_subject_small_normal"):
        return "הגדרה"
    elif type == "source_normal":
        return "מקור"
    elif type == "sub-subject_small":
        return "צמשנה"
    elif type == "fake_sub-subject_small":
        return "צהגדרהמודגשת"
    elif type == "definition_small":
        return "צהגדרה"
    elif type == "source_small":
        return "צמקור"
    elif type == "subject_light":
        return "תערך"
    elif type == "sub-subject_light":
        return "תמשנה"
    elif type in ("definition_light", "unknown_light"):
        return "תהגדרה"
    elif type == "source_light":
        return "תמקור"
    elif type == "s02Symbol":
        return "מעוין"
    elif type == "centered_meuyan":
        return "מעויןמרכזי"
    elif type == "section_title_secondary":
        return "my_section_title_secondary"
    #elif type == "DefaultParagraphFont":
    #    return #TODO: what??
    else:
        # print "TAKALA: ", type
        return "תקלה"


def unite_lines(data, r_prev_line, r_line, prefix_to_new_line = "", suffix_to_new_line = ""):
    global prev_line
    global latex_data

    print("unite_lines. removing: ", prev_line)

    # remove 'prev_line'
    latex_data = latex_data.replace(prev_line, "")
    data = data.replace(prev_line, "")

    # create united line
    if r_prev_line is not None:
        name = r_prev_line.group(2) + ' \protect\\\\ ' + prefix_to_new_line + r_line.group(2) + suffix_to_new_line
        simple_name = r_prev_line.group(2) + ' ' + r_line.group(2)
        line = "\\my%s{%s}{%s}" % (r_prev_line.group(1), name, get_section_short_name(simple_name))
    else:
        r_prev_line = re.compile(r"\\my(\w+)\{(.*)\{(.*)\}\}(.*)").match(prev_line)
        line = r"\my%s{%s{%s}}%s" % (r_prev_line.group(1), r_prev_line.group(2), r_prev_line.group(3) + ' \protect\\\\ ' + r_line.group(2), r_prev_line.group(4))

    print("unite_lines. adding: ", line)

    return data, line


prev_line = ""
def add_line_to_data(data, line):
    global prev_line

    # this matches things of either kind:
    # \mychapter{a}{b}    # .group(1) = 'chapter'      , .group(2) = 'a', group(3) = '{b}', group(4) = 'b'
    # \mysubsection{a}    # .group(1) = 'mysubsection' , .group(2) = 'a', group(3) is None, group(4) is None
    r = re.compile(r"\\my(\w+)\{([^{}]+)\}({([^{}]+)\})?", re.UNICODE)
    r_line = r.match(line)
    r_prev_line = r.match(prev_line)

    if line.startswith("\\my") and prev_line.startswith("\\my") and line.split('{')[0] == prev_line.split('{')[0]:
        if r_line.group(1) == r_prev_line.group(1) and r_prev_line.group(2) != 'מדורים':
            # we need to unite prev_line and line
            (data, line) = unite_lines(data, r_prev_line, r_line)

    if line.startswith(r"\my_section_title_secondary"):
        assert prev_line.startswith(r"\my") and "chapter" in prev_line
        (data, line) = unite_lines(data, r_prev_line, r_line, r"\mysectiontitlesecondarysize{", "}")

    if "°" in line:
        line = line.replace("°", "\\mycircle{°}")



    data += line
    prev_line = line
    return data


latex_data = ""
latex_new_lines_in_raw = 0
num_of_heading_titles = 0

in_section_intro = False
letters_section_current_letter = ""

next_define_is_moto = False
next_define_ends_moto = False
moto_line_is_left = False
moto_line_was_left = False



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


def begin_moto_left_line():
    global moto_line_is_left, moto_line_was_left
    moto_line_is_left = True
    moto_line_was_left = True
    return "\leftline{"


def end_moto_left_line():
    global moto_line_is_left
    moto_line_is_left = False
    return "}"


def add_to_latex(para, word_doc_footnotes):
    global latex_new_lines_in_raw
    global latex_data
    global num_of_heading_titles
    global moto_line_is_left
    global moto_line_was_left
    global current_section
    global letters_section_current_letter
    global in_section_intro

    data = ""
    for (i, (type, text)) in enumerate(para):
        data = handle_moto(data, text, type)
        data = handle_intro(data, text, type)

        if 'heading' in type and text.strip():

            # TODO: adjust headings
            if type == 'heading_title':
                get_section_short_name(text)
                if num_of_heading_titles == 0:
                    command = "\\mybookname"
                else:
                    command = "\\mytitle"
                data = add_line_to_data(data, "%s{%s}{%s}" % (command, text, current_section['section']))
                num_of_heading_titles += 1
            elif type == 'heading_section':
                get_section_short_name(text)
                assert not (current_section['moto'] and current_section['intro'])
                next_define_is_moto = current_section['moto']
                if next_define_is_moto:
                    chapter_command = "mymotochapter"
                elif current_section['intro']:
                    in_section_intro = True
                    chapter_command = "myintrochapter"
                else:
                    chapter_command = "mychapter"
                data = add_line_to_data(data, "\\%s{%s}{%s}" % (chapter_command, text, current_section['section']))
            elif type == 'heading_sub-section-bigger':
                data = add_line_to_data(data, "\\mysubsection{%s}" % (text))
            elif type == 'heading_sub-section':
                data = add_line_to_data(data, "\\mysubsection{%s}" % (text))
            elif type == 'heading_letter':
                if current_section['section'] == "מילון הראיה":
                    data = add_line_to_data(data, "\\mylettertitle{%s}" % (text))
                elif current_section['section'] == "פסוקים":
                    data = add_line_to_data(data, "\\myletterweaktitle{%s}" % (text))
                else:
                    data = add_line_to_data(data, "\\myletterslave{%s}" % (text))

            data += "\n"


        elif type == "new_line":
            if next_define_ends_moto and moto_line_is_left and type == "new_line":
                data += end_moto_left_line()


            latex_new_lines_in_raw += 1
            if latex_new_lines_in_raw == 1:
                if data:
                    data += (r"\mynewline")
                else:
                    # we ignore that 'new line', and not adding it to 'data' - so no need to count it
                    latex_new_lines_in_raw = 0
            elif latex_new_lines_in_raw == 2:
                # chop the "new line" symbol - not required before new paragraph
                assert latex_data.endswith(r"\mynewline") or data.endswith(r"\mynewline")
                if data.endswith(r"\mynewline"):
                    data = data[:-(len(r"\mynewline"))]
                elif latex_data.endswith(r"\mynewline"):
                    latex_data = latex_data[:-(len(r"\mynewline"))]
                data += ("\n\n")
            else:
                pass


            if next_define_ends_moto and not moto_line_is_left and not moto_line_was_left and type == "new_line":
                # inside Moto - got to Left section
                data += begin_moto_left_line()


        elif current_section['section'] == "אותיות" and not in_section_intro and type == "subject_normal" and text.strip() != letters_section_current_letter:
            letters_section_current_letter = text.strip()
            data += "\\stamletter{%s}" % text[0]
            data = add_line_to_data(data, "\\%s{%s}" % (latex_type(type), text[1:]))


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
            data = add_line_to_data(data, "\\%s{%s}" % ('footref', text.strip()))


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

    if moto_line_is_left and "leftline" not in data:
        data += end_moto_left_line()

    latex_data += data



def handle_moto(data, text, type):
    global next_define_is_moto, next_define_ends_moto, moto_line_is_left, moto_line_was_left
    if latex_type(type) == "ערך" and next_define_is_moto:
        # starting Moto
        data += begin_moto()
        next_define_is_moto = False
        next_define_ends_moto = True
        moto_line_is_left = False
        moto_line_was_left = False
    elif (('heading' in type and text.strip()) or latex_type(type) == "ערך") and next_define_ends_moto:
        # ending Moto
        data += end_moto()
        next_define_is_moto = False
        next_define_ends_moto = False
        moto_line_is_left = False
        moto_line_was_left = False
    return data


# CSV has too many layers of " protection - it's better just to strip them of...
def csv_text_compare(a, b):
    return a.strip().replace('"', '') == b.strip().replace('"', '')


def handle_intro(data, text, type):
    global in_section_intro
    if in_section_intro and type == current_section['end_of_intro:type'] and csv_text_compare(text, current_section['end_of_intro:text']):
        # print "end of intro: ", current_section['section']
        data += r"\newpage"
        data += r"\setfancyheadtitleboth{%s}" % current_section['section']
        data += r"\resetfootnotecounter"
        in_section_intro = False
    return data



def run_xelatex(f):
    try:
        subprocess.call(['xelatex', f])
    except:
        subprocess.call([r'C:\Users\zharamax\AppData\Local\Programs\MiKTeX 2.9\miktex\bin\x64\xelatex', f])


def close_latex():
    global latex_data
    latex_data = latex_data.replace('"',"״")
    latex_data = latex_data.replace("'","׳")
    latex_data = latex_data.replace("־", "\\hebrewmakaf ")


    os.chdir("tex")

    with open("content.tex", 'a', encoding='utf-8') as latex_file:
        latex_file.write(latex_data)


    # twice because of thumb-indices
    run_xelatex('milon.tex')
    run_xelatex('milon.tex')
#    os.startfile("milon.pdf")
#     os.startfile("milon.tex")
    os.chdir("..")

