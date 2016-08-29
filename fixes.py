# -*- coding: utf-8 -*-

import re
from text_segments import MilonTextSegments as TS, fake
import text_segments as ts

####################################################
# paragraph fixes ##################################
####################################################


def analyze_and_fix(para):
    # unite splitted adjacent similar types
    prev_type, prev_text = None, ""
    new_para = []
    for (raw_type, text_raw) in para:
        text = text_raw.replace("@", "")
        if text == u"◊":
            type = TS.MeUyan
        else:
            type = raw_type
        if prev_type:
            if (type == prev_type) or \
                    (is_subject_small_or_sub_subject(type) and is_subject_small_or_sub_subject(prev_type)) or \
                    (prev_type != TS.footnote and text.strip() in ("", u"°", u"־", ",")):
                prev_text += text
            else:
                new_para.append((prev_type, prev_text))
                prev_type, prev_text = type, text
        else:
            prev_type, prev_text = type, text
    new_para.append((prev_type, prev_text))

    # make new_lines stand on their own
    para = new_para
    new_para = []
    for (type, text) in para:
        lines = text.split("\n")
        if len(lines) > 1:
            for (i, line) in enumerate(lines):
                if line:
                    new_para.append((type, line))
                if i+1 < len(lines):
                    new_para.append((TS.newLine, "\n"))
        else:
            new_para.append((type, text))

    # fix wrong subjects
    para = new_para
    new_para = []
    for (index, (type, text)) in enumerate(para):
        # if 'subject' in type:
        if ts.is_subject(para, index):
            # real subject is either:
            # first
            # after new_line and empty
            # after subject,"-"
            # after Meuyan
            if (index == 0) or (ts.is_prev_newline(para, index)) or (ts.is_prev_meuyan(para, index)):
                new_para.append((type, text))
            elif (ts.is_prev_subject(para, index)):
                new_para.append((make_sub_subject(type), text))
            elif new_para[index-1][0] in (TS.subSubjectNormal, TS.subjectSmall):
                new_para.append((make_sub_subject(type), text))
            else:
                new_para.append((fake(type), text))
        elif 'subject' in type:
            # it's got a subject, but 'is_subject' failed
            new_para.append((fake(type), text))
        else:
            new_para.append((type, text))

    # fix wrong 'source's
    para = new_para
    new_para = []
    source_pattern = re.compile(r"(\s*\[.*\]\s*)")
    for (type, text) in para:
        if type == TS.sourceNormal:
            small = False
            for (chunk) in source_pattern.split(text):
                if source_pattern.match(chunk):
                    if small:
                        new_para.append((TS.sourceSmall, chunk))
                    else:
                        new_para.append((type, chunk))
                elif chunk != "":
                    new_para.append((TS.definitionSmall, chunk))
                    small = True
                # re.split(r"(\[.*\])", s)
        else:
            new_para.append((type, text))

    # make links from circles - °
    para = new_para
    new_para = []
    pattern = re.compile(u"([\S־]*\S+°)", re.UNICODE)
    for (type, text) in para:
        # don't do this for subjects - it complicates their own link name...
        if u"°" in text and 'subject' not in type:
            for (chunk) in pattern.split(text):
                new_para.append((type, chunk))
        else:
            new_para.append((type, text))


    # fix new lines inside headings
    para = new_para
    new_para = []
    ignore_new_line = False
    for (type, text) in para:
        if 'heading' in type:
            ignore_new_line = True
            new_para.append((type, text))
        elif type == TS.newLine and ignore_new_line:
            pass
        else:
            new_para.append((type, text))


    # scan for 'empty subjects' ...
    has_subject = False
    has_definition = False
    for (type, text) in para:
        if 'subject' in type and 'fake' not in type and text.strip():
            has_subject = True
            has_definition = False
        elif 'definition' in type:
            has_definition = True

    # ... and fix 'em if required
    if has_subject and not has_definition:
        # empty subject
        #TODO - might be caused by 'heading' interpreted as subject
        para = new_para
        new_para = []
        for (type, text) in para:
            if 'subject' in type and 'fake' not in type:
                new_para.append((fake(type), text))
            else:
                new_para.append((type, text))


    with open('output/debug_fix.txt', 'a') as debug_file:
        debug_file.write("---------------\n")
        for (type, text) in new_para:
            s = "%s:%s.\n" % (type, text)
            debug_file.write(s.encode('utf8') + ' ')

    # fix
    return new_para

def make_sub_subject(subj):
    if subj == TS.subjectSmall:
        return TS.subSubjectNormal
    else:
        return subj

def is_subject_small_or_sub_subject(s):
    return s in [TS.subjectSmall, TS.subSubjectNormal]


##################################################
# run fixes ######################################
##################################################

def fix_sz_cs(run, type, debug_file):
    result = type
    szCs = run.element.rPr.szCs.attrib.values()[0]
    if szCs == "20" and 'subject' in type:
        if run.style.style_id == "s01":
            s = "!Fixed!szCs=%s:%s." % (szCs, run.text)
            # print s
            debug_file.write(s.encode('utf8') + ' ')
            return TS.subjectSmall
    elif szCs == "22" and type == TS.definitionNormal:
        return TS.subjectNormal
    elif szCs == "16" and type == TS.sourceNormal:
        return TS.sourceSmall
    else:
        pass
    return result

def fix_b_cs(run, type):
    result = type
    try:
        bCs = run.element.rPr.bCs.attrib.values()[0]
        if bCs == "0" and 'subject' in type:
            if type in (TS.subjectSmall, TS.subSubjectNormal):
                return TS.definitionNormal
            else:
                pass
                # print "Unknown b_cs=0"
    except:
        pass
    return result

def fix_unknown(run):
    if run.font.size == 114300 and run.style.style_id == 's04':
        return TS.subjectLight
    elif run.font.size == 101600 and run.style.style_id == 's04' and run.font.cs_bold:
        return TS.subSubjectLight
    elif run.font.size == 101600 and run.style.style_id == 's04' and not run.font.cs_bold:
        return TS.definitionLight
    elif run.font.size is None and run.style.style_id == 's04':
        return TS.definitionLight
    elif run.font.size == 88900 and run.style.style_id == 's04':
        return TS.sourceLight
    else:
        return TS.unknownLight


def fix_DefaultParagraphFont(run):
    # only if it's really a text
    if run.text.strip() and run.text.strip() not in ("-", "(", ")", "[", "]", "'", '"', ","):
        if run.font.size == 152400 and not run.bold:
            return TS.subjectNormal
        if run.font.size == 139700 and run.bold:
            return TS.subjectNormal
        elif run.font.size == 127000:
            return TS.definitionNormal
        elif run.font.size == 114300:
            return TS.sourceNormal
        elif run.font.size == 101600:
            return TS.sourceSmall
        elif run.font.size == 88900:
            return TS.sourceSmall
        elif run.font.size is None and run.bold:
            return TS.subSubjectNormal
        elif run.font.size is None and not run.bold:
            return TS.definitionNormal
        else:
            print "AH!", ":",run.text.strip(),".", run.font.size, run.bold
            assert False
    else:
        return TS.defaultParagraph
