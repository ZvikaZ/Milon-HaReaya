def get_style(run):
    return 'bolded' if run.bold else 'normal'


def analyze_footnote(note):
    result = []

    for i, para in enumerate(note.paragraphs):
        for run in para.runs:
            result.append({
                'text': run.text,
                'style': "sub-subject_small" if get_style(run) == 'bolded' else "definition_small"
            })
        if result[-1]['style'] != 'new_line':
            # dont add at the end ; dont add two consecutive new_lines
            result.append({'text': '\n', 'style': 'new_line'})

    while result and result[-1]['style'] == 'new_line':
        result.pop()

    return result
