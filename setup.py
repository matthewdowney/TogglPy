import codecs
import os
import re

import setuptools

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


long_description = read('README.md')


setuptools.setup(
    name='TogglPy',
    version=find_version('toggl', '__init__.py'),
    description='Python library for interacting with the Toggl API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/matthewdowney/TogglPy',
    author="Matthew Downey",
    author_email='matthewdowney20@gmail.com',
    license='MIT License',
    zip_safe=False,
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='api toggl',
    install_requires=[],
)
