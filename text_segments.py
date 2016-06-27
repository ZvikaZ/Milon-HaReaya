# -*- coding: utf-8 -*-
'''
This module defines the types of text segments in the Milon, in context of style.
Examples:
subject_normal ("אבות")
definition_normal ("החושבים הגדולים של משפחת האדם")
source_normal ("ע"א ד ח ט")
'''

class MilonTextSegments:
	# 'normal' segments
	subjectNormal = 'subject_normal'
	subSubjectNormal = 'sub-subject_normal'
	definitionNormal = 'definition_normal'
	sourceNormal = 'source_normal'

    # 'small' segments
	subjectSmall = 'subject_small'
	definitionSmall = 'definition_small'
	sourceSmall = 'source_small'

    # 'light' segments
	subjectLight = 'subject_light'
	subSubjectLight = 'sub-subject_light'
	definitionLight = 'definition_light'
	unknownLight = 'unknown_light'
	sourceLight = 'source_light'

	# footnote segments
	footnote = 'footnote'
	footnoteRecc = 'footnote_reccurence'

    # misc.
	MeUyan = 's02Symbol',   # ◊
	footnoteRef = 'FootnoteReference'
	endnoteRef = 'EndnoteReference' #?
    
    # this is problematic! has its own function to handle it
	defaultParagraph = 'DefaultParagraphFont'
