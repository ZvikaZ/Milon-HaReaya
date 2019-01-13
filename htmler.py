# in the future, this file will contain much more content
# now it's holding small portion of HTML-related work

import dominate.tags as tags
import footer


def add_footnote_to_output(paragraphs):
    with tags.li():
        for (para) in paragraphs:
            for (run) in para.runs:
                style = footer.get_style(run)
                if style == "bolded":
                    with tags.span(run.text):
                        tags.attr(cls="sub-subject_small")
                else:
                    with tags.span(run.text):
                        tags.attr(cls="definition_small")
            tags.br()



