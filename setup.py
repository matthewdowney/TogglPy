from setuptools import setup, find_packages
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read('README.md')

setup(
    name='TogglPy',
    version=find_version('TogglPy', '__init__.py'),
    description='',
    long_description=long_description,
    url='https://github.com/matthewdowney/TogglPy',
    author="Matthew Downey",
    author_email='matthewdowney20@gmail.com',
    license='Apache Software License',
    zip_safe=False,
    packages=['TogglPy'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='api toggl',
    install_requires=[],
)
