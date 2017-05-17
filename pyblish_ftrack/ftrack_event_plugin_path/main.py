import sys
import contextlib
import subprocess
import argparse

from vendor.Qt import QtWidgets
from vendor.riffle import browser


@contextlib.contextmanager
def application():
    app = QtWidgets.QApplication.instance()

    if not app:
        print("Starting new QApplication..")
        app = QtWidgets.QApplication(sys.argv)
        yield app
        app.exec_()
    else:
        print("Using existing QApplication..")
        yield app


if __name__ == "__main__":

    # Setup arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        action="store",
        default="",
        dest="path"
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        default=False,
        dest="browser",
    )
    args = parser.parse_args()
    results = vars(args)
    print results
    print sys.argv
    with application():

        file_browser = browser.FilesystemBrowser()
        path = results["path"]
        browser = results["browser"]

        # If a path is passed, we'll set this as the current location.
        if path:
            file_browser.setLocation(path)

        # Get path from browser.
        if browser:
            if file_browser.exec_():
                selected = file_browser.selected()
                if selected:
                    path = selected[0]

        # Start pyblish is a path is available.
        if path:
            subprocess.call([
                "python",
                "-m",
                "pyblish_standalone",
                path,
                "--register-host",
                "ftrack",
                "--register-gui",
                "pyblish_lite"
            ])

        sys.exit()
