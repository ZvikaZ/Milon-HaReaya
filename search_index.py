import json
import re
import subprocess
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
                'subject': clean_subject,
                'data': data,
                'footnote_ids': footnote_ids,
                'footnotes': [],
                'section': html_doc.section,
                'url': "%s.html#%s" % (html_doc.index, subject_id)
            })
            db[clean_subject] = new_subject_l
            for id in footnote_ids:
                footnotes_db[int(id)] = clean_subject
        else:
            print("None subject: ", tag)	#TODO fix, or remove


footnote_id = 0


def learn_footnote(paragraphs):
    global footnote_id
    footnote_id += 1
    text = ''.join([p.text for p in paragraphs])
    # try:
    subject = footnotes_db[footnote_id]
    defs = db[subject]
    new_defs = []
    changes = 0
    for d in defs:
        for footnote in d['footnote_ids']:
            if int(footnote) == int(footnote_id):
                d['footnotes'].append(f"{footnote}. {text}")
                changes += 1
        new_defs.append(d)
    # assert changes == 1
    # print(f"changes: {changes}")
    db[subject] = new_defs
    # except:
    #     print("ERROR at footnote: ", id)


def close_html_doc():
    global footnote_id
    footnote_id = 0


def create_index():
    with open('output/create_index.js', 'w', encoding='utf-8') as fp:
        s = json.dumps(db)
        fp.write("data = " + s)
        fp.write("""
        
const elasticlunr = require('./www/elasticlunr.min')
//const elasticlunr = require('./www/elasticlunr')

const fs = require('fs')

var index = elasticlunr(function () {
    this.addField('subject');
    this.addField('data');
    this.addField('footnotes');
    this.setRef('url');
    // this.saveDocument(false);		//depends on size...
});

// quick and dirty Hebrew support - just don't do English processing
//TODO write my own trimmer, to keep only Hebrew/English letters (and numerals?)
index.pipeline.reset();

for (var subject in data) {
	for (var item of data[subject]) {
		//console.log(item);
		index.addDoc(item);
	}
} 

fs.writeFile('www/index.json', "indexDump = " + JSON.stringify(index), function (err) {
	if (err) throw err;
	console.log('index.json written');
});


        """)
    subprocess.run(['node', 'create_index'], cwd='output', shell=True)
