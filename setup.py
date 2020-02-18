from setuptools import setup, find_packages

with open('README.md') as f:
    README = f.read()

setup(
    name='iso19119-nl-parser',
    version='0.0.1',
    description='PDOK service metadata (ISO19119) paraser',
    long_description=README,
    author='Anton Bakker',
    author_email='anton.bakker@kadaster.nl',
    packages=find_packages(exclude=('tests', 'docs')),
    setup_requires=['wheel'],
    install_requires=[
        'lxml==4.2.1'
    ],
    entry_points='''
        [console_scripts]
        parse-md=iso19119_parser.cli:main
    ''',
)
