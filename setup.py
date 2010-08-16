#import ez_setup
#ez_setup.use_setuptools()

from setuptools import setup, find_packages
import sys

def script():
  if sys.platform == 'win32':
    return ['jolt', 'jolt.bat']
  else:
    return ['jolt']

setup(
    name = "jolt",
    version = "0.1",
    packages = find_packages(),
    package_dir = {'':'.'},
    #package_data = {
    #    '': ['data/*'],
    #},
    zip_safe = True,
    install_requires = ["simplejson>=2.1.1"],
    scripts = script(),
    author = "VimJolts Developer Team",
    author_email = "ujihisa+vimjolts2@gmail.com",
    description = "Vim package manager.",
    #license = "",
    keywords = "vim vimscript plugin jolt joltserver",
    url = "http://github.com/vimjolts/vimjolts",
)

