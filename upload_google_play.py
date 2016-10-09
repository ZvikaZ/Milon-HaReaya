"""
Uploads APK file to Google Play, using credentials in secret.py and key.p12

In order to work, I had to manually modify C:\Python27\Lib\site-packages\googleapiclient\discovery.py:
        if media_mime_type is None:
          # 19.1.16 - Zvika - bypass this stupid MIME problem
          #D raise UnknownFileType(media_filename)
          media_mime_type = u'application/vnd.android.package-archive'

"""

# important docs: https://developers.google.com/android-publisher/api-ref/edits/tracks#resource


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
# apk_file = "output/milon.apk"
TRACK = 'production'  # Can be 'alpha', beta', 'production' or 'rollout'

class PlayAPISession:
    def get_service(self):
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
        return service

    def get_edit_id(self):
        edit_request = self.service.edits().insert(body={}, packageName=package_name)
        result = edit_request.execute()
        edit_id = result['id']
        return edit_id

    def __init__(self):
        self.service = self.get_service()
        self.edit_id = self.get_edit_id()

    def commit(self):
        commit_request = self.service.edits().commit(
            editId=self.edit_id, packageName=package_name).execute()
        print 'Edit "%s" has been committed' % (commit_request['id'])


    def upload_apk(self, apk_file):
        service = self.service
        edit_id = self.edit_id
    ###
        try:

            apk_response = service.edits().apks().upload(
                editId=edit_id,
                packageName=package_name,
                media_body=apk_file).execute()

            version_code = apk_response['versionCode']
            print 'Version code %d has been uploaded' % version_code

            return version_code

        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run the '
                   'application to re-authorize')


    def update_track(self, version_codes):
        try:
            track_response = self.service.edits().tracks().update(
                editId=self.edit_id,
                track=TRACK,
                packageName=package_name,
                body={u'versionCodes': version_codes}).execute()

            print 'Track %s is set for version code(s) %s' % (
                track_response['track'], str(track_response['versionCodes']))


        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run the '
                   'application to re-authorize')


    def get_last_apk(self):
        try:
            apks_result = self.service.edits().apks().list(
                editId=self.edit_id, packageName=package_name).execute()

            versions = [apk['versionCode'] for apk in apks_result['apks']]
            versions.sort()
            return versions[-1]


        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run the '
                   'application to re-authorize')


    ### Copied from basic_list_apks_service_account.py:
    def list_all_apks(self):
        try:
            apks_result = self.service.edits().apks().list(
                editId=self.edit_id, packageName=package_name).execute()

            for apk in apks_result['apks']:
                print 'versionCode: %s, binary.sha1: %s' % (
                    apk['versionCode'], apk['binary']['sha1'])

        except client.AccessTokenRefreshError:
            print ('The credentials have been revoked or expired, please re-run the '
                   'application to re-authorize')


    def main(self, apk_files):
        versions = []
        for f in apk_files:
            versions.append(self.upload_apk(f))
        print "Successfully loaded versions:"
        print versions
        self.update_track(versions)
        self.commit()



if __name__ == '__main__':
    playAPISession = PlayAPISession()
    playAPISession.main(["output/milon.x86.apk", "output/milon.arm.apk"])

