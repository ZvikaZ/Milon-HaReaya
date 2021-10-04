import json
import re
import subprocess
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data = ""

    def handle_data(self, data):
        self.data += data.replace("\n", "")


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


def get_subject(tag):
    try:
        if 'subject' in tag.attributes['class']:
            # return tag.attributes['id']
            parser = MyHTMLParser()
            parser.feed(str(tag))
            return parser.data

        else:
            return None
    except KeyError:
        return None


def get_data(tags):
    parser = MyHTMLParser()
    for tag in tags:
        parser.feed(str(tag))
    return parser.data


def learn(tag, html_doc):
    if len(tag.children) >= 2:
        item = {
            'subject': get_subject(tag.children[0]),
            'data': get_data(tag.children[1:])
        }
        if item['subject'] is not None:
            subject = item['subject'].strip()
            clean_subject = clean_name(subject)
            new_subject_l = db.get(clean_subject, [])
            subject_id = calc_subject_id(subject, len(new_subject_l))
            new_subject_l.append({
                'subject': clean_subject,
                'data': item['data'],
                'section': html_doc.section,
                'url': "%s.html#%s" % (html_doc.index, subject_id)
            })
            db[clean_subject] = new_subject_l


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
