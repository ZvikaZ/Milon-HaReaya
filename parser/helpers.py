import re


def uniqify(s):
    return "".join(set(s))


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
        return (is_subject(para, i - 2) and
                (para[i - 1][1].replace('"', '').strip() == "-") or (para[i - 1][0] == "footnote"))
    except:
        return False


def is_prev_newline(para, i):
    try:
        return para[i - 1][0] == "new_line" or (para[i - 2][0] == "new_line" and para[i - 1][1] == "")
    except:
        return False


def is_prev_meuyan(para, i):
    try:
        return para[i - 1][0] == "s02Symbol" or uniqify(para[i - 1][1].strip()) == '◊'
    except:
        return False


def is_subject_small_or_sub_subject(s):
    return s in ['subject_small', 'sub-subject_normal']
