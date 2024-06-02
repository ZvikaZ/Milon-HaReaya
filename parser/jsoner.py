def create_json(pages):
    for page in pages:
        print("***************************")
        for section in page['sections']:
            print(section)