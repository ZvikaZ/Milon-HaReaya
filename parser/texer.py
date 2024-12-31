# TODO use the new 'paragraphs'
# TODO don't split sources to new page
# TODO don't bold ע"ע גאונים, תקופת הגאונים ; ע במדור מונחי קבלה ונסתר
# TODO font swap אוביקטיבי, ע' במדור הכרה
# TODO font reference 11 before אור עליון
# TODO lower the polythumb, similar to printed book
# TODO decrease size of האידאליות הנשמתית
# TODO too many hyphens on נקודת האמונה


import os
import shutil
import subprocess
import codecs
import re


class LatexProcessor:
    def __init__(self):
        self.sections_csv_file = "sections_info.csv"
        self.current_section = {
            "section": None,
            "moto": False,
            "intro": False,
            "end_of_intro:type": "",
            "end_of_intro:text": "",
        }
        self.latex_data = ""
        self.prev_line = ""
        self.num_of_heading_titles = 0
        self.in_section_intro = False
        self.letters_section_current_letter = ""
        self.next_define_is_moto = False
        self.next_define_ends_moto = False
        self.moto_line_is_left = False
        self.moto_line_was_left = False

    def is_bold(self, para):
        print(para, "bolded?", "subject" in para["style"])  # TODO delete
        return "subject" in para["style"]  # TODO is it good?

    def reverse_words(self, s):
        w1 = s.split()
        w2 = reversed(w1)
        return " ".join(w2)

    def get_bool_from_csv(self, cell):
        if cell == "" or cell.lower() == "no":
            return False
        elif cell.lower() == "yes":
            return True
        else:
            print("Illegal value in CSV: ", cell)
            assert False

    # the output is 'reversed' due to some bug in 'fancytabs' that shows the words reversed in the string
    # TODO: report this bug...
    def get_section_short_name(self, section):
        # TODO is all of this CSV relevant? there is no .csv file ; either create one, or delete all of this...

        # I'd prefer to use 'csv' package, but it doesn't behave well with Unicode...
        # with open(sections_csv_file, 'r') as csvfile:

        # the "-sig" is required to ignore BOM (=some sort of Unicode white space)
        csvfile = codecs.open(self.sections_csv_file, encoding="utf-8-sig")
        for row in csvfile:
            s = row.strip().split(",")
            if s[0].replace('"', "").strip() == section.replace('"', "").strip():
                self.current_section["section"] = s[1].strip()
                self.current_section["moto"] = self.get_bool_from_csv(s[2])
                self.current_section["intro"] = self.get_bool_from_csv(s[3])
                self.current_section["end_of_intro:type"] = s[4].strip()
                self.current_section["end_of_intro:text"] = s[5].strip()
                print("CSV found: ", s[1], self.current_section)
                return self.reverse_words(self.current_section["section"])
        print("CSV failed search for: ", section)
        self.current_section["section"] = section
        self.current_section["moto"] = False
        self.current_section["intro"] = False
        self.current_section["end_of_intro:type"] = ""
        self.current_section["end_of_intro:text"] = ""
        return self.reverse_words(self.current_section["section"])

    def open_latex(self):
        os.chdir("input_tex")
        for f in (
            "milon.tex",
            "polythumbs.sty",
            #  "hebrew-gymatria-fix.sty",     # Rav Kalner asked not to do it. Leaving it here for future reference...
        ):
            shutil.copyfile(f, os.path.join("../tex", f))
        os.chdir("../")

    def latex_type(self, type):
        if type in ("subject_normal", "fake_subject_normal"):
            return "ערך"
        elif type in (
            "sub-subject_normal",
            "subject_small",
            "fake_subject_small",
            "fake_sub-subject_normal",
        ):
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
        # elif type == "DefaultParagraphFont":
        #    return #TODO: what??
        else:
            # print "TAKALA: ", type
            return "תקלה"

    def unite_lines(
        self, data, r_prev_line, r_line, prefix_to_new_line="", suffix_to_new_line=""
    ):
        print("unite_lines. removing: ", self.prev_line)

        # remove 'prev_line'
        self.latex_data = self.latex_data.replace(self.prev_line, "")
        data = data.replace(self.prev_line, "")

        # create united line
        if r_prev_line is not None:
            name = (
                r_prev_line.group(2)
                + " \protect\\\\ "
                + prefix_to_new_line
                + r_line.group(2)
                + suffix_to_new_line
            )
            simple_name = r_prev_line.group(2) + " " + r_line.group(2)
            line = "\\my%s{%s}{%s}" % (
                r_prev_line.group(1),
                name,
                self.get_section_short_name(simple_name),
            )
        else:
            r_prev_line = re.compile(r"\\my(\w+)\{(.*)\{(.*)\}\}(.*)").match(
                self.prev_line
            )
            line = r"\my%s{%s{%s}}%s" % (
                r_prev_line.group(1),
                r_prev_line.group(2),
                r_prev_line.group(3) + " \protect\\\\ " + r_line.group(2),
                r_prev_line.group(4),
            )

        print("unite_lines. adding: ", line)

        return data, line

    def add_line_to_data(self, data, line):
        # this matches things of either kind:
        # \mychapter{a}{b}    # .group(1) = 'chapter'      , .group(2) = 'a', group(3) = '{b}', group(4) = 'b'
        # \mysubsection{a}    # .group(1) = 'mysubsection' , .group(2) = 'a', group(3) is None, group(4) is None
        r = re.compile(r"\\my(\w+)\{([^{}]+)\}({([^{}]+)\})?", re.UNICODE)
        r_line = r.match(line)
        r_prev_line = r.match(self.prev_line)

        if (
            line.startswith("\\my")
            and self.prev_line.startswith("\\my")
            and line.split("{")[0] == self.prev_line.split("{")[0]
        ):
            if (
                r_line.group(1) == r_prev_line.group(1)
                and r_prev_line.group(2) != "מדורים"
            ):
                # we need to unite prev_line and line
                (data, line) = self.unite_lines(data, r_prev_line, r_line)

        if line.startswith(r"\my_section_title_secondary"):
            assert self.prev_line.startswith(r"\my") and "chapter" in self.prev_line
            (data, line) = self.unite_lines(
                data, r_prev_line, r_line, r"\mysectiontitlesecondarysize{", "}"
            )

        if "°" in line:
            line = line.replace("°", "\\mycircle{°}")

        data += line
        self.prev_line = line
        return data

    def begin_moto(self):
        return """
        \\end{multicols}
        \\thispagestyle{empty}
        \\vspace*{0.2cm}
        \\begin{adjustbox}{minipage=8cm,margin=0pt \\smallskipamount,center}
        """

    def end_moto(self):
        return """
        \\end{adjustbox} 
        \\clearpage
        \\begin{multicols}{2}
        """

    def begin_moto_left_line(self):
        self.moto_line_is_left = True
        self.moto_line_was_left = True
        return "\\leftline{"

    def end_moto_left_line(self):
        self.moto_line_is_left = False
        return "}"

    def add_to_latex(self, para):
        data = ""
        for i, (type, text) in enumerate(para["items"]):
            data = self.handle_moto(data, text, type)
            data = self.handle_intro(data, text, type)

            if "heading" in type and text.strip():
                # TODO: adjust headings
                if type == "heading_title":
                    self.get_section_short_name(text)
                    if self.num_of_heading_titles == 0:
                        command = "\\mybookname"
                    else:
                        command = "\\mytitle"
                    data = self.add_line_to_data(
                        data,
                        "%s{%s}{%s}" % (command, text, self.current_section["section"]),
                    )
                    self.num_of_heading_titles += 1
                elif type == "heading_section":
                    self.get_section_short_name(text)
                    assert not (
                        self.current_section["moto"] and self.current_section["intro"]
                    )
                    self.next_define_is_moto = self.current_section["moto"]
                    if self.next_define_is_moto:
                        chapter_command = "mymotochapter"
                    elif self.current_section["intro"]:
                        self.in_section_intro = True
                        chapter_command = "myintrochapter"
                    else:
                        chapter_command = "mychapter"
                    data = self.add_line_to_data(
                        data,
                        "\\%s{%s}{%s}"
                        % (chapter_command, text, self.current_section["section"]),
                    )
                elif type == "heading_sub-section-bigger":
                    data = self.add_line_to_data(data, "\\mysubsection{%s}" % (text))
                elif type == "heading_sub-section":
                    data = self.add_line_to_data(data, "\\mysubsection{%s}" % (text))
                elif type == "heading_letter":
                    if self.current_section["section"] == "מילון הראיה":
                        data = self.add_line_to_data(
                            data, "\\mylettertitle{%s}" % (text)
                        )
                    elif self.current_section["section"] == "פסוקים":
                        data = self.add_line_to_data(
                            data, "\\myletterweaktitle{%s}" % (text)
                        )
                    else:
                        data = self.add_line_to_data(
                            data, "\\myletterslave{%s}" % (text)
                        )

                data += "\n"

            elif type == "new_line":
                if (
                    self.next_define_ends_moto
                    and self.moto_line_is_left
                    and type == "new_line"
                ):
                    data += self.end_moto_left_line()

                data = data.strip() + "\n\n"

                if (
                    self.next_define_ends_moto
                    and not self.moto_line_is_left
                    and not self.moto_line_was_left
                    and type == "new_line"
                ):
                    # inside Moto - got to Left section
                    data += self.begin_moto_left_line()

            elif (
                self.current_section["section"] == "אותיות"
                and not self.in_section_intro
                and type == "subject_normal"
                and text.strip() != self.letters_section_current_letter
            ):
                self.letters_section_current_letter = text.strip()
                data += "\\stamletter{%s}" % text[0]
                data = self.add_line_to_data(
                    data, "\\%s{%s}" % (self.latex_type(type), text[1:])
                )

            elif type == "footnote":
                id = int(text)
                footnote = para["footnotes"][id]
                assert footnote["number_relative"] == id

                all_runs_list = []
                for foot_para in footnote["content"]:
                    foot_text = ""
                    if self.is_bold(foot_para):
                        foot_text += "\\%s{%s}" % ("textbf", foot_para["text"])
                    else:
                        foot_text += foot_para["text"]
                    all_runs_list.append(foot_text)

                # all_runs_text = "\\newline\n".join(all_runs_list)     #TODO when do we need newline?
                all_runs_text = "".join(all_runs_list)  # TODO is it good?
                data = self.add_line_to_data(
                    data,
                    "\\%s{%s\\label{%s}}"
                    % ("myfootnote", all_runs_text, footnote["number_abs"]),
                )

            elif type == "footnote_recurrence":
                data = self.add_line_to_data(
                    data, "\\%s{%s}" % ("footref", text.strip())
                )

            # # TODO if enabled, it sticks source together, which is good, but it causes strange behavior
            # elif "source" in type:
            #     data = self.add_line_to_data(
            #         data, "\\%s{%s}" % (self.latex_type(type), text.replace(" ", "~"))
            #         # data, r"\samepage{\%s{%s}}" % (self.latex_type(type), text)
            #     )

            # elif is_subject(para, i):
            #     if not is_prev_subject(para, i):
            #         # tags.p()
            #         #tags.br()
            #         pass
            #     subject(html_doc, type, text)
            else:
                # regular(type, text)
                data = self.add_line_to_data(
                    data, "\\%s{%s}" % (self.latex_type(type), text)
                )

        if self.moto_line_is_left and "leftline" not in data:
            data += self.end_moto_left_line()

        self.latex_data += data

    def handle_moto(self, data, text, type):
        if self.latex_type(type) == "ערך" and self.next_define_is_moto:
            # starting Moto
            data += self.begin_moto()
            self.next_define_is_moto = False
            self.next_define_ends_moto = True
            self.moto_line_is_left = False
            self.moto_line_was_left = False
        elif (
            ("heading" in type and text.strip()) or self.latex_type(type) == "ערך"
        ) and self.next_define_ends_moto:
            # ending Moto
            data += self.end_moto()
            self.next_define_is_moto = False
            self.next_define_ends_moto = False
            self.moto_line_is_left = False
            self.moto_line_was_left = False
        return data

    # CSV has too many layers of " protection - it's better just to strip them of...
    def csv_text_compare(self, a, b):
        return a.strip().replace('"', "") == b.strip().replace('"', "")

    def handle_intro(self, data, text, type):
        if (
            self.in_section_intro
            and type == self.current_section["end_of_intro:type"]
            and self.csv_text_compare(text, self.current_section["end_of_intro:text"])
        ):
            # print "end of intro: ", current_section['section']
            data += r"\newpage"
            data += r"\setfancyheadtitleboth{%s}" % self.current_section["section"]
            data += r"\resetfootnotecounter"
            self.in_section_intro = False
        return data

    def run_xelatex(self, f, check=True):
        subprocess.run(
            ["xelatex", "-file-line-error", "-interaction=nonstopmode", f], check=check
        )

    def close_latex(self):
        self.latex_data = self.latex_data.replace('"', "״")
        self.latex_data = self.latex_data.replace("'", "׳")
        self.latex_data = self.latex_data.replace("־", "\\hebrewmakaf ")

        os.chdir("tex")
        with open("content.tex", "a", encoding="utf-8") as latex_file:
            latex_file.write(self.latex_data)

        # twice because of thumb-indices
        self.run_xelatex("milon.tex", check=False)
        self.run_xelatex("milon.tex")
        #        os.startfile("milon.pdf")
        #        os.startfile("milon.tex")
        os.chdir("..")


def create_pdf(parsed_data):
    processor = LatexProcessor()
    processor.open_latex()
    for para in parsed_data:
        processor.add_to_latex(para)
    processor.close_latex()
