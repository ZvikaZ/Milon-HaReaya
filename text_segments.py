# -*- coding: utf-8 -*-
'''
This module defines the types of text segments in the Milon, in context of style.
Examples:
subject_normal ("אבות")
definition_normal ("החושבים הגדולים של משפחת האדם")
source_normal ("ע"א ד ח ט")
'''
import re

class MilonTextSegments:
	# 'normal' segments
	subjectNormal = 'subject_normal'
	subSubjectNormal = 'sub-subject_normal'
	definitionNormal = 'definition_normal'
	sourceNormal = 'source_normal'

    # 'small' segments
	subjectSmall = 'subject_small'
	subSubjectSmall = 'sub-subject_small'
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
	footnoteRec = 'footnote_recurrence'

    # misc.
	MeUyan = 's02Symbol',   # ◊
	footnoteRef = 'FootnoteReference'
	endnoteRef = 'EndnoteReference' #?
	unknown = 'unknown'
	newLine = 'new_line'

    # this is problematic! has its own function to handle it
	defaultParagraph = 'DefaultParagraphFont'

def fake(segment=''):
	return "fake_" + segment

def is_subject(para, i, next=False):
    type, text = para[i]
    # print "is? ", type, text.strip()
    # if 'subject' in type and not re.search(r"\w", text, re.UNICODE):
    #     print "!", text
    # print "is?", type, text, i, ('subject' in type and re.search(r"\w", text, re.UNICODE))

    # if 'subject' in type and re.search(r"\w", text, re.UNICODE) and i>0:
    #     p_type, p_text = para[i-1]
    #     print "?", i-1, p_type, p_text
    return 'subject' in type and re.search(r"\w", text, re.UNICODE) and 'fake' not in type

def is_prev_subject(para, i):
    try:
        return (is_subject(para, i-2) and
                (para[i-1][1].replace('"','').strip() == "-") or (para[i-1][0] == TS.foonote))
    except:
        return False

def is_prev_newline(para, i):
    try:
        return para[i-1][0] == "new_line" or (para[i-2][0] == "new_line" and para[i-1][1] == "")
    except:
        return False

def is_prev_meuyan(para, i):
    try:
        return para[i-1][0] == TS.MeUyan
    except:
        return False
