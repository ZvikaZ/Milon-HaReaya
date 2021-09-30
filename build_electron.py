import os.path
import pathlib
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

    shutil.copy2(pathlib.Path("electron_builder") / "dist" / "Setup Milon HaReaya.exe", "output")
    subprocess.run(pathlib.Path("output") / "Setup Milon HaReaya.exe")


if __name__ == '__main__':
    build_electron()
