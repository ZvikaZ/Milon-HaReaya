import requests

from helpers import sectionize_in_pages, prepare_search
from secret import TOKEN_URL, WRITE_API_KEY, API_URL


def get_token():
    url = TOKEN_URL
    write_api_key = WRITE_API_KEY

    response = requests.post(url, json={"key": write_api_key})
    return response.json().get("access_token")


def fetch_data(endpoint, data):
    token = get_token()

    url = f"{API_URL}/{endpoint}"

    try:
        result = requests.post(url, json=data, headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        })
        return result.json()
    except Exception as err:
        print("Error fetching data:", err)


def upload(collection, docs):
    print(f"inserting {len(docs)} documents...")
    result = fetch_data("update", {
        "collection": collection,
        "data": docs,
    })
    print(result)


def adapt_and_upload(pages):
    pages = [sectionize_in_pages(page) for page in pages]
    sections = [section for page in pages for section in page['sections']]
    sections = [prepare_search(section) for section in sections]

    upload('pages', pages)
    upload('sections', sections)


    toc = [{'title': p['name'],
            'appear_in_toc': p['appear_in_toc'],
            'key': p['key']
            } for p in pages]
    upload('misc', [{'key': 'toc', 'data': toc}])
