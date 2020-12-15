import winshell
from pathlib import Path


def startup_dir_location():
    return str(Path(winshell.folder('CSIDL_STARTUP')))


def desktop_location():
    return str(Path(winshell.desktop()))


class CreateShortcut:

    def __init__(self, shortcut_base_location="", shortcut_name="", file_base_location="", file_name="",
                 description=""):
        self.shortcut_base_location = shortcut_base_location
        self.shortcut_name = shortcut_name
        self.file_base_location = file_base_location
        self.file_name = file_name
        self.description = description

    def create_shortcut(self):
        shortcut_path = str(Path(self.shortcut_base_location, self.shortcut_name))
        file_path = str(Path(self.file_base_location, self.file_name))
        with winshell.shortcut(shortcut_path) as link:
            link.path = file_path
            link.working_directory = self.file_base_location
            link.description = self.description
            # you can also pass argument to run
            # link.arguments = "-m winshell"
