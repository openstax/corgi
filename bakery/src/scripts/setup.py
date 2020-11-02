# -*- coding: utf-8 -*-
from setuptools import setup
import os

HERE = os.path.abspath(os.path.dirname(__file__))


def parse_requirements(req_file):
    """Parse a requirements.txt file to a list of requirements"""
    with open(req_file, 'r') as fb:
        reqs = [
            req.strip() for req in fb.readlines()
            if req.strip() and not req.startswith('#')
        ]
    return list(reqs)


install_requires = parse_requirements(os.path.join(HERE, 'requirements.txt'))
tests_require = [
    'pytest',
    'pytest-mock',
    'pytest-cov',
    'flake8',
    'requests-mock'
]
extras_require = {
    'test': tests_require,
}

# Boilerplate arguments
SETUP_KWARGS = dict(
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    packages=['bakery_scripts'],
    include_package_data=True,
)

# Note, this package is not to be released to PyPI and is for interal usage
# only
setup(
    name='cops-bakery-scripts',
    version='0.0.1',
    author='OpenStax Content Engineering',
    url="https://github.com/openstax/output-producer-service",
    license='AGPLv3.0',
    package_dir={"bakery_scripts": "."},
    entry_points={
        'console_scripts': [
            'assemble-meta = bakery_scripts.assemble_book_metadata:main',
            'link-extras = bakery_scripts.link_extras:main',
            'link-single = bakery_scripts.link_single:main',
            'bake-meta = bakery_scripts.bake_book_metadata:main',
            'disassemble = bakery_scripts.disassemble_book:main',
            'checksum = bakery_scripts.checksum_resource:main',
            'jsonify = bakery_scripts.jsonify_book:main',
            'check-feed = bakery_scripts.check_feed:main',
            'copy-resources-s3 = bakery_scripts.copy_resources_s3:main',
            'gdocify = bakery_scripts.gdocify_book:main',
            'upload-docx = bakery_scripts.upload_docx:main',
            'mathmltable2png = bakery_scripts.mathmltable2png:main'
        ]
    },
    **SETUP_KWARGS,
)
