import os.path
import shutil
import subprocess


def build_electron():
    try:
        shutil.rmtree(os.path.join("electron_builder", "dist"))
    except FileNotFoundError:
        pass

    try:
        shutil.rmtree(os.path.join("electron_builder", "www"))
    except FileNotFoundError:
        pass

    shutil.copytree(os.path.join("output", "www"), os.path.join("electron_builder", "www"))

    subprocess.run(['yarn'], cwd='electron_builder', shell=True)
    subprocess.run(['yarn', 'dist'], cwd='electron_builder', shell=True)


if __name__ == '__main__':
    build_electron()