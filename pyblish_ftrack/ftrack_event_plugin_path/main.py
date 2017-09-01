import os
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
        default=os.getcwd(),
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

    with application():

        path = results["path"]

        # Get path from browser.
        if results["browser"]:
            file_browser = browser.FilesystemBrowser(path)
            file_browser.setLocation(path)

            if file_browser.exec_():
                selected = file_browser.selected()
                if selected:
                    path = selected[0]

        # Add "ftrack" as host through environment variable.
        os.environ["PYBLISH_HOSTS"] = "ftrack"

        # Start pyblish gui. We can't set the current working directory because
        # UNC paths does not work with cmd.exe, so we inject to the context
        # instead.
        subprocess.call(
            [
                sys.executable,
                "-m",
                "pyblish",
                "--data",
                "currentFile",
                path,
                "gui"
            ]
        )

        sys.exit()
