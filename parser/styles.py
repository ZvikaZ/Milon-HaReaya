from helpers import uniqify

styles = {
    's01': 'subject_normal',
    's11': 'sub-subject_normal',
    's03_bold': 'sub-subject_small',  # ?Fixing appendix  ?
    's02': 'definition_normal',
    's02_bold': 'definition_normal',  # ?Fixing appendix
    's03': 'definition_small',
    'Heading3Char': 'definition_normal',
    '1': 'definition_normal',  # ?
    'FootnoteTextChar1': 'definition_normal',  # ?
    'HebrewChar': 'definition_normal',  # ?

    # this is problematic! has its own function to handle it
    'DefaultParagraphFont': 'DefaultParagraphFont',
    'DefaultParagraphFont_bold': 'DefaultParagraphFont',  # TODO: correct?

    's15': 'subject_small',
    's17': 'subject_small',
    's1510': 'subject_small',
    's1510_bold': 'subject_small',
    's05': 'definition_small',
    's05_bold': 'sub-subject_small',  # ?Fixing appendix
    's038': 'source_small',
    's0590': 'source_small',
    's050': 'source_small',
    '050': 'source_small',

    's149': 'subject_light',
    's14': 'subject_light',
    's16': 'sub-subject_light',
    's12_bold': 'sub-subject_light',
    's168': 'sub-subject_light',
    's048': 'definition_light',
    's12': 'definition_light',
    's04': 'unknown_light',
    's127': 'source_light',

    's02Symbol': 's02Symbol',  # MeUyan

    'FootnoteReference': 'FootnoteReference',
    'EndnoteReference': 'EndnoteReference',  # ?

    # 17.3.19 - these were added with new Office 365 (2019) - seem like new aliases for existing styles
    'a0': 'DefaultParagraphFont',
    'a0_bold': 'DefaultParagraphFont',
    'a3': 'FootnoteReference',
    'a7': 'EndnoteReference',
    '30': 'definition_normal',
    '11': 'definition_normal',
    'a6': 'definition_normal',
    # \17.3.19
}


# support old and new version of docx
# new is preferred, because, well, it's new...
# old is preferred because I'm using a branch with footnotes support
def run_style_id(run):
    bold = ""
    if run.text.strip() and run.font.cs_bold:
        # print "BOLD: ", run.bold, run.font.bold, run.font.cs_bold, ": ", run.text
        bold = "_bold"
    try:
        return run.style.style_id + bold
    except:
        if run.style:
            return run.style + bold
        else:
            return 'DefaultParagraphFont' + bold


# if the actual size is greater
class Sizes:
    my_dict = {
        381000: 'heading_title',
        330200: 'heading_section',  # e.g., "Tora"
        279400: 'heading_sub-section-bigger',  # e.g., "Mehkarim Beurim"
        215900: 'heading_sub-section',  # e.g., "Avraham Yitzhak VeYaakov"
        177800: 'heading_letter',
        165100: 'normal',  # 152400
    }

    # yeah, it's not nice and programmaticish to have this twice
    # but it's more efficient :)
    normal = 165100

    def match(self, size):
        if size > self.normal:
            return self.my_dict.get(size, "unknown")
        else:
            return 'normal'

    def get_heading_type(self, kind):
        assert 'heading' in kind
        if kind == 'heading_title':
            return 'h1'
        elif kind == 'heading_section':
            return 'h2'
        elif kind == 'heading_sub-section-bigger' or kind == 'section_title_secondary':
            return 'h3'
        elif kind == 'heading_sub-section':
            return 'h4'
        elif kind == 'heading_letter':
            return 'h5'
        else:
            assert False


sizes = Sizes()

temp_l = []


def bold_type(s, type, run):
    if type == 'definition_normal' and run.font.size == 139700:
        return 'subject_normal'
    elif type == 'definition_normal':
        return 'subject_small'
    elif type == 'source_normal' and run.style.style_id == "s03":
        return 'sub-subject_small'
    elif type == "definition_small" and run.style.style_id == "s05":
        return 'sub-subject_small'
    elif type == 'source_normal' and run.style.style_id == "DefaultParagraphFont" and run.font.size == 139700:
        return 'subject_normal'
    elif type == 'source_normal' and run.style.style_id == "DefaultParagraphFont" and run.font.size != 139700:
        return 'sub-subject_normal'
    elif type == 'source_small' and run.style.style_id == "a0" and run.font.size == 101600:
        return 'subject_small'
    elif type == 'unknown_light' and run.style.style_id == "s04" and run.font.size == 114300:
        return 'subject_light'
    elif type == 'unknown_light' and run.style.style_id == "s04" and run.font.size == 101600:
        return 'sub-subject_light'
    elif type == 'definition_light' and run.style.style_id == "s12" and run.font.size == 101600:
        return 'sub-subject_light'
    elif type == 'definition_light' and run.style.style_id == "s04" and run.font.size is None:
        return 'subject_light'
    elif type == 'definition_light' and run.style.style_id == "s12" and run.font.size is None:
        # TODO - verify that it's always OK
        return 'sub-subject_light'
    elif type == 'source_normal':
        print("Strange 'source_normal' bold!")
        return type
    elif type == 'source_small':
        print("Strange 'source_small' bold!")
        return type
    elif 'subject' in type or 'heading' in type:
        return type
    elif uniqify(run.text.strip()) in ("◊", "-", ""):
        return type
    else:
        if type not in temp_l:
            print("Unexpected bold!", type)
            print(s, type, run.text, run.font.size, run.style.style_id)
            # assert False      #TODO return this assert, fix the occurence
            temp_l.append(type)
        return type
