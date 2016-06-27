# -*- coding: utf-8 -*-
'''
This module translates docx codes to abstract text segment types.
'''

from text_segments import MilonTextSegments as TS

docxCode2segType = {
    's01': TS.subjectNormal,
    's11': TS.subSubjectNormal,
    's02': TS.definitionNormal,
    's03': TS.sourceNormal,
    'Heading3Char': TS.definitionNormal,
    '1': TS.definitionNormal,   #?
    'FootnoteTextChar1': TS.definitionNormal,   #?
    'HebrewChar': TS.definitionNormal,   #?

    # this is problematic! has its own function to handle it
    'DefaultParagraphFont': TS.defaultParagraph,

    's15': TS.subjectSmall,
    's17': TS.subjectSmall,
    's1510': TS.subjectSmall,
    's05': TS.definitionSmall,
    's038': TS.sourceSmall,
    's0590': TS.sourceSmall,
    's050': TS.sourceSmall,
    '050': TS.sourceSmall,

    's149': TS.subjectLight,
    's14': TS.subjectLight,
    's16': TS.subSubjectLight,
    's168': TS.subSubjectLight,
    's048': TS.definitionLight,
    's12': TS.definitionLight,
    's04': TS.unknownLight,
    's127': TS.sourceLight,

    's02Symbol': TS.MeUyan,   # MeUyan

    'FootnoteReference': TS.footnoteRef,
    'EndnoteReference': TS.endnoteRef, #?
}
