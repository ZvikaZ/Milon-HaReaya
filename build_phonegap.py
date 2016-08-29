"""
push_to_phonegap(zipfile)
 sends the zipfile to PhoneGap Build, using credentials found in secret.py
 polls for APK file to be ready, and downloads it
"""
import requests
import json
import sys
import time
import shutil
from milon_zip import MilonZipper

try:
    from secret import *
except:
    print "Missing 'secret.py'. Cannot build with Phonegap"
    # secret.py should contain these:
    # auth = ('your@mail.com', "password")
    # key_json = 'data={"key_pw":"password","keystore_pw":"password"}'

# ## Optional HTTP logging
# import logging
#
# # These two lines enable debugging at httplib level (requests->urllib3->http.client)
# # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # The only thing missing will be the response.body which is not logged.
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1
#
# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True
# ##


class MilonPhoneGapBuilder(MilonZipper):
    def __init__(self, zipper):
        self.zipper = zipper

    def start(self):
        self.zipper.start()

    def add(self, paragraph, footnotes, size_kind):
        self.zipper.add(paragraph, footnotes, size_kind)

    def finish(self):
        self.zipper.finish()
        push_to_phonegap(self.zipper.get_zip_path())


base_url = 'https://build.phonegap.com/'
api_url = base_url + 'api/v1/'
app_url = api_url + "apps/1852495/"
key_url = api_url + "keys/android/158873"

requests.packages.urllib3.disable_warnings()


def check_app_status():
    r = requests.get(app_url, verify=False, auth=auth)
    assert r.status_code == 200
    resp = json.loads(r.text)
    status = resp['status']['android']
    if status == 'error':
        print "APK creation Error: ", resp['error']
        sys.exit(1)
    elif status not in ('pending', 'complete'):
        print "\nAPK creation status:"
        print status
        print resp
    else:
        # print "APK creation status:", status
        pass
    return status


def push_to_phonegap(zipfile):
    # # get my info w/o token
    # r = requests.get(base_url + "api/v1/me", verify=False,
    #                  auth=auth)
    # print r.status_code
    # print r.text

    # # create token
    # r = requests.post(base_url + "/token", verify=False, auth=auth)
    # assert r.status_code == 200
    # resp = json.loads(r.text)
    # token = resp['token']
    #
    # # use token to get my info
    # r = requests.get(base_url + "api/v1/me?auth_token=%s" % token, verify=False)
    # print r.status_code, r.text


    r = requests.put(base_url + "api/v1/keys/android/158873",
                      headers={'Content-Type': 'application/x-www-form-urlencoded'},
                      data=key_json, verify=False, auth=auth)
    # resp = json.loads(r.text)
    # print "Unlock resp:", r.status_code, r.text
    assert r.status_code == 202

    # sys.exit(1)

    r = requests.get(base_url + "api/v1/keys/android/158873", verify=False, auth=auth)
    # resp = json.loads(r.text)
    # print "Unlock get resp:", r.status_code, r.text
    # # print 'j:', r.json()
    assert r.status_code == 200
    assert not r.json()['locked']

    # upload zip file
    files = {'file': open(zipfile, 'rb')}
    r = requests.put(app_url, files=files, verify=False, auth=auth)
    assert r.status_code == 200
    # print "Upload status: ", r.status_code, r.text

    print "Compiling APK"
    while check_app_status() == 'pending':
        print "Pending"
        time.sleep(1)


    # download the APK
    print "Downloading APK"
    r = requests.get(app_url+"android", verify=False, auth=auth)
    assert r.status_code == 200

    with open('milon.apk', 'wb') as f:
        f.write(r.content)
    shutil.move("milon.apk", "output/")
    print "milon.apk downloaded"



if __name__ == '__main__':
    push_to_phonegap("output/milon.zip")