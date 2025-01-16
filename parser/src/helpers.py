import os
import re
import shutil

# from rftokenizer import RFTokenizer   #TODO


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


keys = {}


def create_key(page, cur_section):
    try:
        page_name_1, page_name_2 = page['name']
        page_name = f'{page_name_1}-{page_name_2}'
    except ValueError:
        page_name = page['name']

    key = f"{page_name.strip()}__{cur_section['title'].strip()}"
    if key not in keys:
        keys[key] = 0
    keys[key] += 1
    return f'{key}_{keys[key]}'


def sectionize_in_pages(page, keep_items=False):
    page['key'] = create_key(page, {'title': 'page'})
    print(page['key'])
    page['sections'] = []
    cur_section = {'title': '', 'content': []}
    for kind, value in page['items']:
        if kind == 'new_line' and value.count('\n') > 1:
            cur_section['key'] = create_key(page, cur_section)
            page['sections'].append(cur_section)
            cur_section = {'title': '', 'content': []}
        elif 'heading' in kind:
            assert cur_section['title'] == ''
            cur_section['title'] = value
        elif 'footnote' in kind:
            print(kind, value)  # TODO del
            note = page['footnotes'][int(value)]
            value = note
        elif 'subject' in kind:
            cur_section['title'] += value
        cur_section['content'].append((kind, value))
    cur_section['key'] = create_key(page, cur_section)
    page['sections'].append(cur_section)

    if not keep_items:
        del page['items']

    return page


def create_dirs():
    try:
        shutil.rmtree("output")
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree("tex")
    except FileNotFoundError:
        pass

    os.mkdir("output")
    os.mkdir("tex")


def clean_non_letters(text):
    text = ''.join(char if char.isalpha() or char.isspace() else ' ' for char in text)
    text = ' '.join(text.split())
    text += ' '
    return text


# TODO, use, or remove
# tokenizer = RFTokenizer(model="heb")
# print(tokenizer)
#
#
# def tokenize(text):
#     print('starting tokenization')
#     print(text)
#     result = tokenizer.rf_tokenize(text.replace(" ", "\n"))
#     result = [re.sub(r'.*\|', '', s) for s in result] # not good if there is a Vav at end of word, it leaves only it
#     print(result)
#     print('finished tokenization')
#     return result


def prepare_search(section):
    section['raw_subject'] = ""
    section['raw_text'] = ""
    section['raw_footnote'] = ""
    for type, value in section['content']:
        if 'subject' in type:
            section['raw_subject'] += clean_non_letters(value)
        elif 'footnote' in type:
            for ft_part in value['content']:
                section['raw_footnote'] += clean_non_letters(ft_part['text'])
        elif 'source' not in type:
            section['raw_text'] += clean_non_letters(value)
    # TODO use, improve, or remove
    # for f in ['raw_subject', 'raw_text', 'raw_footnote']:
    #     section[f + '_tokens'] = tokenize(section[f]) if section[f] else ''

    return section


def is_paren_or_space(s):
    return s.strip() in ("-", "(", ")", "[", "]", "'", '"', ",", ".", "")
