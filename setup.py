from setuptools import setup

import os

requirements_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')

with open(requirements_filename) as fd:
    install_requires = [i.strip() for i in fd.readlines()]

requirements_dev_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'requirements-dev.txt')

with open(requirements_filename) as fd:
    tests_require = [i.strip() for i in fd.readlines()]

long_description_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'README.md')

with open(long_description_filename) as fd:
    long_description = fd.read()

setup(
    name='fierce',
    version='1.4.0',
    description='A DNS reconnaissance tool for locating non-contiguous IP space.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mschwager/fierce',
    packages=['fierce'],
    package_dir={'fierce': 'fierce'},
    license='GPLv3',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Security',
    ],
    install_requires=install_requires,
    tests_require=tests_require,
    python_requires='>=3.0',
    entry_points={
        'console_scripts': [
            'fierce = fierce.fierce:main',
        ],
    },
    package_data={
        'fierce': [
            'lists/*.txt',
        ],
    },
)
