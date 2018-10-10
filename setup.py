from pathlib import Path
from shutil import copytree
from shutil import rmtree
from sys import prefix

from setuptools import setup

try:
    with open('.version') as f:
        VERSION = f.readline().strip()
except IOError:
    VERSION = 'unknown'

scripts_folders = ['acct', 'bin', 'desktop', 'makeservices',
                   'net', 'printing', 'sbin', 'staff', 'sys']

scripts_root = Path(prefix) / 'utils'
if scripts_root.exists():
    rmtree(scripts_root)
scripts_root.mkdir()

for dir in scripts_folders:
    bin_dir = scripts_root / dir
    copytree(Path('.') / dir, bin_dir)

setup(
    name='ocf-utils',
    version=VERSION,
    url='https://www.ocf.berkeley.edu/',
    author='Open Computing Facility',
    author_email='sm+packages@ocf.berkeley.edu',
)
