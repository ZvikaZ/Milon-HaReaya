'''
This module takes care of the issue of sizes in the document.
'''
from text_segments import MilonTextSegments as TS, fake
import dominate
import dominate.tags as tags

my_dict = {
    381000: 'heading_title',
    330200: 'heading_section',              # e.g., "Tora"
    279400: 'heading_sub-section-bigger',   # e.g., "Mehkarim Beurim"
    215900: 'heading_sub-section',          # e.g., "Avraham Yitzhak VeYaakov"
    177800: 'heading_letter',
    165100: 'normal',               # 152400
}

# yeah, it's not nice and programmaticish to have this twice
# but it's more efficient :)
normal = 165100

def match(size):
    if size > normal:
        return my_dict.get(size, TS.unknown)
    else:
        return 'normal'

def get_heading_type(kind):
    if kind == 'heading_title':
        return tags.h1
    elif kind == 'heading_section':
        return tags.h2
    elif kind == 'heading_sub-section-bigger':
        return tags.h3
    elif kind == 'heading_sub-section':
        return tags.h4
    elif kind == 'heading_letter':
        return tags.h5