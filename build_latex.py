# -*- coding: utf-8 -*-
'''
Module for creating the latex document of the milon.
'''
from build import *
from text_segments import MilonTextSegments as TS, fake
import shutil


class MilonLatexBuilder(MilonBuilder):
	'''
	'''
	def __init__(self, input_dir, output_dir):
		MilonBuilder.__init__(self, input_dir, output_dir)
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

	def add(self, para, f, sk): # f and sk have no use
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
			