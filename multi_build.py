# -*- coding: utf-8 -*-
'''
This module is an aggregator of 'builder' modules.
You should add all the builders to this builder, and they all should have start() finish() and add() functions.
Then you can use this builder aggregator as it was a single builder, and simply add paragraphs, one by one to this builder.
All the corner cases and exceptions should be delt with internally by the builders aggregated by this builder.
'''
from build import *

class MilonMultiBuilder(MilonBuilder):
	def __init__(self):
		self.builders = []

	def addBuilder(self, builder):
		self.builders.append(builder)

	def start(self):
		for b in self.builders:
			b.start()

	def add(self, para, footnotes, size_kind):
		for b in self.builders:
			b.add(para, footnotes, size_kind)

	def finish(self):
		for b in self.builders:
			b.finish()
