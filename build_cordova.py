"""
In order to update Android version, try:
    # cordova platform remove android
    # cordova platform add android@11.X.X
    and if needed, https://stackoverflow.com/a/70634241/1543290
"""

import subprocess
import shutil
import pathlib
from distutils.dir_util import copy_tree

import upload_google_play
from misc import replace_in_file
import secret


def prepare_cordova():
    subprocess.run("cordova platform add android".split(), cwd='input_cordova', shell=True)
    copy_tree("input_cordova", "output")


def build_cordova():
    keystore = secret.apk_sign_keystore_file
    storePassword = secret.apk_sign_storePassword
    alias = secret.apk_sign_alias
    password = secret.apk_sign_password
    subprocess.run(
        f"cordova build --debug --release -- --keystore={keystore} --storePassword={storePassword} --alias={alias} --password={password} --packageType=apk".split(),
        cwd='output', shell=True)
    shutil.copy2(pathlib.Path(
        "output") / "platforms" / "android" / "app" / "build" / "outputs" / "apk" / "release" / "app-release.apk"
                 , pathlib.Path("output") / "milon.apk")


def update_apk_version():
    try:
        playAPISession = upload_google_play.PlayAPISession()
        version_code = playAPISession.get_last_apk() + 1
        replace_in_file('output/config.xml', 'UPDATED_BY_SCRIPT_VERSION_CODE', str(version_code))
    except Exception as e:
        print("Couldn't connect to Google Play - .apk version not updated!")
        print(e)


def main():
    prepare_cordova()
    update_apk_version()
    build_cordova()


if __name__ == '__main__':
    main()
