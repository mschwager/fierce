from setuptools import setup

import os

requirements_filename = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')

with open(requirements_filename) as fd:
    install_requires = [i.strip() for i in fd.readlines()]

data_files_lists = [os.path.join('lists', l) for l in os.listdir('lists')]

setup(
    name='fierce',
    version='1.1.2',
    description='A DNS reconnaissance tool for locating non-contiguous IP space.',
    url='https://github.com/mschwager/fierce',
    py_modules=['fierce'],
    license='GPLv3',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Security',
    ],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'fierce = fierce:main',
        ],
    },
    data_files=[
        ('lists', data_files_lists),
    ],
)
