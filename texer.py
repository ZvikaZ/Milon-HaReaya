# -*- coding: utf-8 -*-

# hopefully, some day, this file will contain much more of tex-related code

import os
import subprocess
import codecs
import footer

sections_csv_file = "sections_short_names.csv"


def reverse_words(s):
    w1 = s.split()
    w2 = reversed(w1)
    return ' '.join(w2)

# the output is 'reversed' due to some bug in 'fancytabs' that shows the words reversed in the string
# TODO: report this bug...
def get_section_short_name(section):
    # with open(sections_csv_file, 'r') as csvfile:
    csvfile = codecs.open(sections_csv_file, encoding='utf-8')
    for row in csvfile:
        s = row.strip().split(',')
        if s[0].strip('"') == section:
            return reverse_words(s[1])
    return reverse_words(section)




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
                data += ("\\addPolythumb{%s}" % get_section_short_name(text))
            elif type == 'heading_section':
                data += ("\\chapter{%s}" % text)
                data += ("\\addPolythumb{%s}" % get_section_short_name(text))
            elif type == 'heading_sub-section-bigger':
                data += ("\\subsection{%s}" % text)
            elif type == 'heading_sub-section':
                data += ("\\subsection{%s}" % text)
            elif type == 'heading_letter':
                data += ("\\subsubsection{%s}" % text)
                data += ("\\replacePolythumb{%s}" % get_section_short_name(text))

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
            data += ("\\%s{%s}" % (type, all_runs_text))

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



def run_xelatex(f):
    try:
        subprocess.call(['xelatex', f])
    except:
        subprocess.call([r'C:\Users\zharamax\AppData\Local\Programs\MiKTeX 2.9\miktex\bin\x64\xelatex', f])


def close_latex():
    os.chdir("tex")
    # twice because of thumb-indices
    run_xelatex('milon.tex')
    run_xelatex('milon.tex')
    os.startfile("milon.pdf")
    os.chdir("..")

