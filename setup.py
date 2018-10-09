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

scripts_root = Path(prefix) / 'utils'
scripts_root.mkdir(exist_ok=True)

bin_dir = scripts_root / 'bin'
rmtree(bin_dir, ignore_errors=True)

sbin_dir = scripts_root / 'sbin'
rmtree(sbin_dir, ignore_errors=True)

copytree('./bin', bin_dir)
copytree('./sbin', sbin_dir)

setup(
    name='ocf-utils',
    version=VERSION,
    url='https://www.ocf.berkeley.edu/',
    author='Open Computing Facility',
    author_email='sm+packages@ocf.berkeley.edu',
)
