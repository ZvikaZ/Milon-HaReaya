import json
import re
import uuid
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = ""
        self.footnote_ids = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and attrs[0] == ('class', 'ptr'):
            assert attrs[1][0] == 'text'
            number = attrs[1][1]
            self.footnote_ids.append(number)

    def handle_data(self, data):
        self.data += data.replace("\n", "")

    def get_results(self):
        return self.data, self.footnote_ids


def calc_subject_id(text_orig, cnt):
    # subject_id = "subject_%d" % len(subjects_db)
    text = text_orig.replace(" ", "-")
    if cnt == 0:
        return text
    else:
        return "%s%d" % (text, cnt)


def clean_name(s):
    s = re.sub("־", " ", s, flags=re.UNICODE)
    s = re.sub('-', " ", s, flags=re.UNICODE)
    return re.sub(r"[^\w ]", "", s, flags=re.UNICODE)


db = {}
footnotes_db = {}


def get_subject(tag):
    try:
        if 'subject' in tag.attributes['class']:
            # return tag.attributes['id']
            parser = MyHTMLParser()
            parser.feed(str(tag))
            return parser.get_results()

        else:
            return None, []
    except KeyError:
        try:
            return get_subject(tag.children[0])
        except IndexError:
            return None, []


def get_data(tags):
    parser = MyHTMLParser()
    for tag in tags:
        parser.feed(str(tag))
    return parser.get_results()


def get_footnote_key(index, id):
    return str(index) + "&&" + str(id)


def learn(tag, html_doc):
    if len(tag.children) >= 2:
        subject, subject_footnote_ids = get_subject(tag.children[0])
        data, data_footnote_ids = get_data(tag.children[1:])
        footnote_ids = subject_footnote_ids + data_footnote_ids
        if subject is not None:
            subject = subject.strip()
            clean_subject = clean_name(subject)
            new_subject_l = db.get(clean_subject, [])
            subject_id = calc_subject_id(subject, len(new_subject_l))
            new_subject_l.append({
                'id': str(uuid.uuid4()),
                'subject_t': clean_subject,
                'data_t': data,
                'footnote_ids_ss': footnote_ids,
                'footnotes_t': '',
                'section_s': html_doc.section,
                'url_s': "%s.html#%s" % (html_doc.index, subject_id)
            })
            db[clean_subject] = new_subject_l
            for id in footnote_ids:
                footnote_key = get_footnote_key(html_doc.index, id)
                # TODO now we ignore duplicates - do we want to keep them as well?
                if footnote_key not in footnotes_db:
                    footnotes_db[footnote_key] = clean_subject
        else:
            if data.strip():
                print("None subject: ", tag)	 # TODO fix, or remove


footnote_id = 0


def learn_footnote(paragraphs, html_doc_index):
    global footnote_id
    footnote_id += 1
    text = ''.join([p.text for p in paragraphs])
    try:
        subject = footnotes_db[get_footnote_key(html_doc_index, footnote_id)]
        defs = db[subject]
        new_defs = []
        changes = 0
        for d in defs:
            for footnote in d['footnote_ids_ss']:
                if int(footnote) == int(footnote_id):
                    d['footnotes_t'] += (f"\n{footnote}. {text}")
                    changes += 1
            new_defs.append(d)
        db[subject] = new_defs
    except KeyError:
        print(f"learn_footnote: KeyError ({html_doc_index}, {footnote_id}): {text}")       # TODO fix


def close_html_doc():
    global footnote_id
    footnote_id = 0


def create_index():
    with open('output/docs_to_index.json', 'w', encoding='utf-8') as fp:
        flat = [item for sublist in db.values() for item in sublist]
        json.dump(flat, fp)

