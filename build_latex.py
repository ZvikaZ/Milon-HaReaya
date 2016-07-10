# -*- coding: utf-8 -*-
'''
Module for creating the latex document of the milon.
'''
import shutil


class MilonLatexBuilder():
	'''
	'''
	def __init__(self, input_dir, output_dir):
		self.input_dir = input_dir
		self.output_dir = output_dir
		self.latex_new_lines_in_raw = 0

	def delete_output_dir(self):
		try:
			shutil.rmtree(self.output_dir)
		except:
			pass

	def recreate_output_dir(self):
		# delete the current output dir
		self.delete_output_dir()
		# create the output dir
		shutil.copytree(self.input_dir, self.output_dir)

	def start(self):
		self.recreate_output_dir()

	def finish(self):
		# close latex file
		os.chdir("tex")
		# twice because of thumb-indices
		subprocess.call(['xelatex', 'milon.tex'])
		subprocess.call(['xelatex', 'milon.tex'])
		os.startfile("milon.pdf")
		os.chdir("..")

	def add(self, para):
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


			elif type == TS.newLine:
				self.latex_new_lines_in_raw += 1
				if self.latex_new_lines_in_raw == 1:
					if data:
						data += ("\\\\")
				elif self.latex_new_lines_in_raw == 2:
					data += ("\n\n")
				else:
					pass

			elif type == TS.footnote:
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

			if type != TS.newLine:
				self.latex_new_lines_in_raw = 0

		with open(self.output_dir + "/content.tex", 'a') as latex_file:
			latex_file.write(data.encode('utf8'))



######################################################################
### latex ############################################################
######################################################################


def open_latex():
    pass
    # nothing to do here...


def latex_type(type):
    if type == TS.subjectNormal:
        return u"ערך"
    elif type in (TS.subSubjectNormal, TS.subjectNormal, fake(TS.subjectSmall), fake(TS.subSubjectNormal)):
        return u"משנה"
    elif type in (TS.definitionNormal, "fake_subject_small_normal"):
        return u"הגדרה"
    elif type == TS.sourceNormal:
        return u"מקור"
    elif type == TS.subSubjectSmall:
        return u"צמשנה"
    elif type == TS.definitionSmall:
        return u"צהגדרה"
    elif type == TS.sourceSmall:
        return u"צמקור"
    elif type == TS.footnote:
        return TS.footnote    #TODO: improve footnote
    elif type == TS.MeUyan:
        return u"מעוין"
    #elif type == "DefaultParagraphFont":
    #    return #TODO: what??
    else:
        return u"תקלה"



latex_new_lines_in_raw = 0
def add_to_latex(para):
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


        elif type == TS.newLine:
            latex_new_lines_in_raw += 1
            if latex_new_lines_in_raw == 1:
                if data:
                    data += ("\\\\")
            elif latex_new_lines_in_raw == 2:
                data += ("\n\n")
            else:
                pass

        elif type == TS.footnote:
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

        if type != TS.newLine:
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
