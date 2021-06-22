#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = ['pytest>=3', ]

setup(
    author="msk-mind",
    author_email='CompOncBST@mskcc.org',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Pathology Whole Slide Image (WSI) processing pipeline for computational oncology",
    entry_points={
        'console_scripts': [
            'luna_pathology=luna_pathology.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='luna_pathology',
    name='luna_pathology',
    packages=find_packages(include=['luna_pathology', 'luna_pathology.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/msk-mind-apps/luna_pathology',
    version='0.1.0',
    zip_safe=False,
)
