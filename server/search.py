#!/usr/bin/python3
import os
from urllib import request, parse

SUBJECT_WEIGHT = 10
FOOTNOTE_WEIGHT = 0.5

print("Content-type: text/json\n\n")

try:
    (_, method), (_, term) = parse.parse_qsl(os.environ['QUERY_STRING'])

except:
    method = None
    term = 'search.py parse error'

# parens required for multi-word phrases
term = '(' + parse.quote(term) + ')'

if method == 'everywhere':
    term_search = f'q=subject_t%3A{term}%5E{SUBJECT_WEIGHT}%20OR%20data_t%3A{term}%20OR%20footnotes_t%3A{term}%5E{FOOTNOTE_WEIGHT}'
else:
    term_search = f'q=subject_t%3A{term}'

connection = request.urlopen(
    # f'http://localhost:8983/solr/milon/select?fl=*,score&hl.fl=*&hl.requireFieldMatch=true&hl=true&indent=true&q.op=AND&{term_search}&rows=1000&useParams=')
    f'http://localhost:8983/solr/milon/select?fl=*,score&indent=true&q.op=AND&{term_search}&rows=1000&useParams=')
print(connection.read().decode('utf-8'))
