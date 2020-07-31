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
    'flake8'
]
extras_require = {
    'test': tests_require,
}

# Boilerplate arguments
SETUP_KWARGS = dict(
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    packages=['scripts'],
    include_package_data=True,
)

# Note, this package is not to be released to PyPI and is for interal usage only
setup(
    name='cops-bakery-scripts',
    version='0.0.1',
    author='OpenStax Content Engineering',
    url="https://github.com/openstax/output-producer-service",
    license='AGPLv3.0',
    package_dir={"scripts": "."},
    entry_points={
        'console_scripts': [
            'assemble-meta = scripts.assemble_book_metadata:main',
            'link-extras = scripts.link_extras:main',
            'bake-meta = scripts.bake_book_metadata:main',
            'disassemble = scripts.disassemble_book:main',
            'checksum = scripts.checksum_resource:main',
            'jsonify = scripts.jsonify_book:main',
            'check-feed = scripts.check_feed:main',
            'copy-resources-s3 = scripts.copy_resources_s3:main'
        ]
    },
    **SETUP_KWARGS,
)
