import subprocess
import os

import pyblish


path = os.path.join(os.path.dirname(__file__), 'pyblish_util.py')

executable = os.path.dirname(os.path.dirname(pyblish.__file__))
executable = os.path.dirname(os.path.dirname(os.path.dirname(executable)))
executable = os.path.dirname(executable)
executable = os.path.join(executable, 'bin', 'python.bat')

args = [executable, path]
subprocess.Popen(args)
