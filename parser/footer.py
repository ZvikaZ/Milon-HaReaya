# this file will hold footnote analyzing code

def get_style(run):

    # these are not working, because "docx_fork_ludoo" is on old fork :-(
    # however, currently they aren't needed.
    # let's hope this situation will continue...
    # if I will need them in the future, I will have to merge the forks myself

    # try:
    #     hint_cs = run.element.rPr.rFonts.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hint', None) == 'cs'
    # except:
    #     hint_cs = False
    #
    # try:
    #     szCs = run.element.rPr.szCs.attrib.values()[0]
    # except:
    #     szCs = None


    if run.style == 's03' and run.bold != True:
        return "normal"
    elif run.style is None and run.bold is None:
        return "normal"
    elif run.style == 's02' and run.bold is None:
        return "normal"
    elif run.style == 's05' and run.bold is None:
        return "normal"
    elif run.style == 'Emphasis' and run.bold is None:
        return "normal"

    elif run.style == 's03' and run.bold == True:
        return "bolded"
    elif run.style == 's05' and run.bold == True:
        return "bolded"
    elif run.style is None and run.bold == True:
        return "bolded"
    else:
        if run.text.strip():
            print("FOOTNOTE undefined:", run.style, run.bold, " : ", run.text)
        return "normal"