"""
Uploads APK file to Google Play, using credentials in secret.py and key.p12
"""


import apiclient
import httplib2
from oauth2client import client

try:
    from secret import SERVICE_ACCOUNT_EMAIL
except:
    print "Missing 'secret.py'. Cannot upload to Google Play"
    # you probably need also key.p12
    # secret.py should contain something like:
    # SERVICE_ACCOUNT_EMAIL = (
    # 'service-...@api-...gserviceaccount.com')


package_name = "com.haramaty.zvika.milon"
apk_file = "output/milon.apk"
TRACK = 'beta'  # Can be 'alpha', beta', 'production' or 'rollout'

def main():
    # Load the key in PKCS 12 format that you downloaded from the Google APIs
    # Console when you created your Service account.
    f = file('key.p12', 'rb')
    key = f.read()
    f.close()

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with the Credentials. Note that the first parameter, service_account_name,
    # is the Email address created for the Service account. It must be the email
    # address associated with the key that was created.
    credentials = client.SignedJwtAssertionCredentials(
        SERVICE_ACCOUNT_EMAIL,
        key,
        scope='https://www.googleapis.com/auth/androidpublisher')
    http = httplib2.Http()
    http = credentials.authorize(http)

    service = apiclient.discovery.build('androidpublisher', 'v2', http=http)

###
    try:
        edit_request = service.edits().insert(body={}, packageName=package_name)
        result = edit_request.execute()
        edit_id = result['id']

        apk_response = service.edits().apks().upload(
            editId=edit_id,
            packageName=package_name,
            media_body=apk_file).execute()

        print 'Version code %d has been uploaded' % apk_response['versionCode']

        track_response = service.edits().tracks().update(
            editId=edit_id,
            track=TRACK,
            packageName=package_name,
            body={u'versionCodes': [apk_response['versionCode']]}).execute()

        print 'Track %s is set for version code(s) %s' % (
            track_response['track'], str(track_response['versionCodes']))

        commit_request = service.edits().commit(
            editId=edit_id, packageName=package_name).execute()

        print 'Edit "%s" has been committed' % (commit_request['id'])

    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run the '
               'application to re-authorize')
###

    ### This code is working!
    ### Leaving it here for reference
    ### Copied from basic_list_apks_service_account.py:
    ###
    # try:
    #     edit_request = service.edits().insert(body={}, packageName=package_name)
    #     result = edit_request.execute()
    #     edit_id = result['id']
    #
    #     apks_result = service.edits().apks().list(
    #         editId=edit_id, packageName=package_name).execute()
    #
    #     for apk in apks_result['apks']:
    #       print 'versionCode: %s, binary.sha1: %s' % (
    #           apk['versionCode'], apk['binary']['sha1'])
    #
    # except client.AccessTokenRefreshError:
    #     print ('The credentials have been revoked or expired, please re-run the '
    #            'application to re-authorize')



if __name__ == '__main__':
    main()