import sys
import contextlib
import subprocess

from vendor.Qt import QtWidgets
import riffle.browser


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

    with application():

        browser = riffle.browser.FilesystemBrowser()

        # If a path is passed, we'll set this as the current location.
        path = None
        if len(sys.argv) > 1:
            path = sys.argv[1]
            browser.setLocation(sys.argv[1])

        # Get path from browser.
        if browser.exec_():
            selected = browser.selected()
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
