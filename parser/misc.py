def replace_in_file(file_name, orig_str, new_str):
    with open(file_name, 'r', encoding='utf-8') as file:
        filedata = file.read()

    filedata = filedata.replace(orig_str, new_str)

    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(filedata)