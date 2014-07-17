from distutils.core import setup
import py2exe

setup(console=['interfacetest.py'])
# remember to create a csv called 'domainname.csv' in the same directory if you have made a new executable.
# you need py2exe and Python 2.6.5 for this to work.