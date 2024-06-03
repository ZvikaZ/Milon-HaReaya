import requests

from helpers import sectionize
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


def upload(collection, pages):
    print(f"inserting {len(pages)} documents...")
    result = fetch_data("update", {
        "collection": collection,
        "data": pages,
    })
    print(result)


def adapt_and_upload(pages):
    pages = [sectionize(page) for page in pages]
    # for page in pages:
    #     print("***************************")
    #     print(page['name'])
    #     print(page['appear_in_toc'])
    #     print(page['footnote_ids'])
    #     for section in page['items']:
    #         print(section)
    upload('pages', pages)
