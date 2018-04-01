import os
from setuptools import setup
import sys
import subprocess
from os import getcwd
from pathlib import Path

# Get Python path - works in virtualenv, too
python_path = subprocess.Popen([
    "which",
    "python"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    close_fds=True).communicate()[0].rstrip().decode("utf-8")
# print(python_path)
python_path = os.path.dirname(os.path.dirname(python_path))


APP = ['django_cherry.py']
DATA_FILES = ['static', 'db.sqlite3']

OPTIONS = {'argv_emulation': False,
           'strip': True,
           'iconfile': './ark-logo.png.icns',
           'packages':["ArkFund", "ark_fund", 'django'],
           'bdist_base':str(Path(Path(getcwd()).parent))+ '/build', 
           'dist_dir':str(Path(Path(getcwd()).parent)) + '/dist'
           }
print(OPTIONS)
setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
