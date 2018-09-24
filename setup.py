import pathlib
import shutil
import sys

from setuptools import setup

try:
    with open('.version') as f:
        VERSION = f.readline().strip()
except IOError:
    VERSION = 'unknown'

scripts_root = pathlib.Path(sys.prefix) / 'utils'
scripts_root.mkdir(exist_ok=True)

bin_dir = scripts_root / 'bin'
shutil.rmtree(bin_dir, ignore_errors=True)

sbin_dir = scripts_root / 'sbin'
shutil.rmtree(sbin_dir, ignore_errors=True)

shutil.copytree('./bin', bin_dir)
shutil.copytree('./sbin', sbin_dir)

setup(
    name='ocf-utils',
    version=VERSION,
    url='https://www.ocf.berkeley.edu/',
    author='Open Computing Facility',
    author_email='help@ocf.berkeley.edu',
)
