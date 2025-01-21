from helpers import is_paren_or_space


def get_fonts(run):
    try:
        return run.element.rPr.rFonts.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}cs',
                                                 None)
    except:
        return None


def fix_sz_cs(run, type):
    result = type
    szCs = list(run.element.rPr.szCs.attrib.values())[0]

    try:
        eastAsia = 'eastAsia' in list(run.element.rPr.rFonts.attrib.values())
    except:
        eastAsia = False

    try:
        hint_cs = 'cs' in list(run.element.rPr.rFonts.attrib.values())
    except:
        hint_cs = False

    if szCs == "20" and "subject" in type and run.style.style_id == "s01":
        return "subject_small"
    elif szCs == "20" and run.style.style_id == "s03" and hint_cs and run.bold and run.font.cs_bold:
        return "sub-subject_normal"
    elif szCs == "22" and run.style.style_id == "s02" and hint_cs and run.bold and run.font.cs_bold:
        return 'subject_normal'
    elif szCs == "22" and run.style.style_id == "s03" and hint_cs and run.bold:
        return 'subject_normal'
    elif szCs == "22" and type == 'definition_normal':
        return 'subject_normal'
    elif szCs == "22" and type == 'sub-subject_normal':
        return 'subject_normal'
    elif szCs == "14" and type == 'definition_light':
        return 'source_light'
    elif szCs == "16" and type == 'definition_small' and run.text.replace(',', '').replace(':', '').strip().isdigit():
        return 'definition_small'  # keep original type
    elif szCs == "16" and type == 'definition_small':  # and hint_cs:
        return 'source_small'
    elif szCs == "14" and type == 'definition_small' and hint_cs:  # or maybe my 'isdigit'
        return 'source_small'
    elif szCs == "16" and type == 'source_normal' and eastAsia:
        return 'source_small'
    elif szCs == "16" and type == 'source_normal' and hint_cs:
        return 'source_small'
    elif szCs == "14" and type == 'source_normal' and hint_cs:
        return 'source_small'
    elif szCs == "18" and get_fonts(run) == "Miriam" and run.font.cs_bold:
        return 'subject_light'
    elif szCs == "16" and get_fonts(run) == "Miriam" and run.font.cs_bold:
        return 'sub-subject_light'
    elif szCs == "16" and get_fonts(run) == "Miriam":
        return 'definition_light'
    elif szCs == "16" and run.style.style_id == "s16":
        return 'sub-subject_light'
    elif szCs == "14" and get_fonts(run) == "Miriam":
        return 'source_light'
    elif szCs == "18" and type == 'definition_normal':
        return 'definition_small'
    elif szCs == "18" and type == 'sub-subject_normal':
        # return 'sub-subject_normal'             #20.11.16 - Trying to fix Appendix' bold and fonts
        return 'sub-subject_small'
    elif szCs == "18" and type == 'subject_small':
        return 'sub-subject_small'
    elif szCs == "18" and type == 'subject_normal':
        return 'definition_small'
    elif szCs == "18" and type == 'source_normal':
        return 'definition_small'
    elif szCs == "18" and type == 'source_small':
        return 'definition_small'
    elif szCs == "20" and type == 'unknown_light':
        return 'definition_normal'
    elif szCs == "20" and type == 'definition_small':
        return 'definition_normal'
    elif szCs == "26" and type == 'subject_normal':
        ## wild guess, might break everything :-(
        ## be careful here...
        print("ZZ: Fixed to 'section_title_secondary': ", run.text.strip())
        return 'section_title_secondary'
    elif run.text.strip() and run.text.strip() not in ['◊', '°']:
        # print("fix_sz_cs::Unsupported value: ", szCs, "type:", type, ". At: ", run.text)    #TODO: clean this!!!
        pass
    else:
        pass
    return result


def fix_b_cs(run, type):
    result = type
    try:
        bCs = list(run.element.rPr.bCs.attrib.values())[0]
        try:
            hint_cs = run.element.rPr.rFonts.attrib.get(
                '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hint', None) == 'cs'
        except:
            hint_cs = False

        try:
            szCs = list(run.element.rPr.szCs.attrib.values())[0]
        except:
            szCs = None

        try:
            fonts = get_fonts(run)
        except:
            fonts = None

        if bCs == "0" and 'subject' in type:
            if (run.style.style_id == "s01" and fonts != "Narkisim" and (
                    run.bold != True or hint_cs or szCs == '20')) or \
                    (run.style.style_id == "s11" and (run.bold != True or (bCs == '0' and fonts != "Narkisim"))):
                if type in ('subject_small', 'sub-subject_normal'):
                    return 'definition_normal'
            else:
                # print("Unknown b_cs=0")
                pass
    except:
        pass
    return result


def fix_misc_attrib(run, type):
    if get_fonts(run) == "Miriam":
        if type == "definition_small":
            type = "subject_light"

    try:
        eastAsia = list(run.element.rPr.rFonts.attrib.values())[0] == 'eastAsia'
        if eastAsia:
            if type == "source_normal":
                return "definition_small"
            else:
                # print type, run.text
                return type
        else:
            return type

    except:
        return type


def fix_unknown(run):
    if run.font.size == 114300 and run.style.style_id == 's04':
        return 'subject_light'
    elif run.font.size == 101600 and run.style.style_id == 's04' and run.font.cs_bold:
        return 'sub-subject_light'
    elif run.font.size == 101600 and run.style.style_id == 's04' and not run.font.cs_bold:
        return 'definition_light'
    elif run.font.size is None and run.style.style_id == 's04':
        return 'definition_light'
    elif run.font.size == 88900 and run.style.style_id == 's04':
        return 'definition_light'
    else:
        if run.text != '◊':
            print("UNKNOWN: ", run.text)
        return 'unknown_light'


def fix_DefaultParagraphFont(run):
    if run.font.size == 330200:
        return 'heading_section'
    elif run.font.size == 177800 and run.font.cs_bold:
        return 'subject_normal'
    elif run.font.size == 152400 and run.font.cs_bold:
        return 'sub-subject_normal'
    elif run.font.size == 152400 and not run.font.cs_bold:
        return 'definition_normal'
    elif run.font.size == 139700 and run.font.cs_bold:
        return 'subject_normal'
    elif run.font.size == 139700 and not run.font.cs_bold:
        return 'definition_normal'
    elif run.font.size == 127000:
        return 'definition_normal'
    elif run.font.size == 114300 and run.font.cs_bold:
        return 'sub-subject_normal'
    elif run.font.size == 114300 and run.font.bold:
        return 'definition_normal'
    elif run.font.size == 114300 and not run.font.cs_bold:
        return 'source_normal'
    elif run.font.size == 101600 and run.font.bold and run.font.cs_bold:
        return 'subject_small'
    elif run.font.size == 101600:
        return 'source_small'
    elif run.font.size == 88900:
        return 'source_small'
    elif run.font.size == 76200 and run.font.cs_bold is None:
        return 'source_small'
    elif run.font.size is None and run.font.cs_bold:
        return 'sub-subject_normal'
    elif run.font.size is None and not run.font.cs_bold:
        return 'definition_normal'
    else:
        if not is_paren_or_space(run.text.strip()):
            print("fix_DefaultParagraphFont failed:", run.text.strip(), ".", run.font.size, run.bold, run.font.cs_bold)
            # print(paragraph.text)
            assert False


def fix_section_name(name):
    if name == "מילון הראיה":
        return "ערכים כלליים"
    else:
        return name


def fix_newlines_with_spaces_between(items):
    'unite consecutive newlines with white spaces between them to a single newline'
    result = []
    section = []

    for item in items:
        # If we're currently building a section
        if section:
            if item[0] == "new_line":  # Section ends with new_line
                newlines = sum(x[1].count("\n") for x in section) + item[1].count("\n")
                result.append(["new_line", "\n" * newlines])
                section = []
            elif item[1].strip():  # Non-empty item breaks the section
                result.extend(section)
                result.append(item)
                section = []
            else:  # Empty item continues the section
                section.append(item)
        # Not in a section
        elif item[0] == "new_line":  # Start new section
            section = [item]
        else:  # Regular item
            result.append(item)

    # Don't forget remaining items
    if section:
        result.extend(section)

    return result