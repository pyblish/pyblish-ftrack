import sys
import os
import subprocess

from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
import pyblish


class FileBrowser(QWidget):

    def __init__(self):
        super(FileBrowser, self).__init__()

        folder = QFileDialog.getExistingDirectory (self, 'Open folder')

        if folder:

            executable = os.path.dirname(os.path.dirname(pyblish.__file__))
            executable = os.path.dirname(os.path.dirname(executable))
            executable = os.path.dirname(os.path.dirname(executable))
            executable = os.path.join(executable, 'bin', 'python.bat')
            path = os.path.join(os.path.dirname(__file__),
                                'pyblish_executable.py')
            args = [executable, path]
            subprocess.Popen(args, cwd=folder)

        sys.exit()

def main():

    app = QApplication(sys.argv)
    ex = FileBrowser()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
