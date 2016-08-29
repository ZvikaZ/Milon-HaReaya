# -*- coding: utf-8 -*-

import zipfile
import os
from build_html import *

class MilonZipper(MilonHTMLBuilder):
	'''
	'Decorator' for html builder. Not only building the milon's documents, but also zippes them. 
	'''
	def __init__(self, html_builder, zip_file_name):
		self.builder = html_builder
		self.zip_file_name = zip_file_name

	def start(self):
		self.builder.start()

	def add(self, paragraph, footntoes, size_kind):
		self.builder.add(paragraph, footntoes, size_kind)

	def finish(self):
		self.builder.finish()
		self.zip_milon()

	def get_zip_path(self):
		return os.path.join(self.builder.output_dir, self.zip_file_name)

	def zip_milon(self):
		prev_dir = os.getcwd()
		with zipfile.ZipFile(self.zip_file_name, "w", zipfile.ZIP_DEFLATED) as zf:
			os.chdir(self.builder.output_dir)
			for dirname, subdirs, files in os.walk("."):
				# avoid creating 'output' directory as first hierrarchy
				# suddenly causes problem with phonegap - makes garbages APKs...
				zf.write(dirname)
				for filename in files:
					if not 'debug' in filename:
						zf.write(os.path.join(dirname, filename))
			print "Created %s" % self.zip_file_name
		os.chdir(prev_dir)

		shutil.move(self.zip_file_name, self.builder.output_dir)
