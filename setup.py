from codecs import StreamReader, open
from os.path import dirname, join, realpath

from setuptools import setup

cwd = dirname(realpath(__file__))

##
# Load long description for PyPi.
with open(join(cwd, 'README.rst'), 'r', 'utf-8') as f:  # type: StreamReader
    long_description = f.read()

##
# Off we go!
setup(
    name='phx-class-registry',
    description='Factory+Registry pattern for Python classes.',
    url='https://class-registry.readthedocs.io/',

    version='3.0.5',

    packages=['class_registry'],

    long_description=long_description,

    install_requires=[],

    extras_require={
        'docs-builder': ['sphinx', 'sphinx_rtd_theme'],
        'test-runner':  ['tox >= 3.7'],
    },

    test_suite='test',
    test_loader='nose.loader:TestLoader',
    tests_require=['nose'],

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='registry pattern',

    author='Phoenix Zerin',
    author_email='phx@phx.ph',
)
