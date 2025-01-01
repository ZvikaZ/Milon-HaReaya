# this file will hold footnote analyzing code

def get_style(run):
    return 'bolded' if run.bold else 'normal'


def analyze_footnote(note):
    result = []
    for (para) in note.paragraphs:
        for (run) in para.runs:
            result.append({
                'text': run.text,
                'style': "sub-subject_small" if get_style(run) == 'bolded' else "definition_small"
            })
    return result
