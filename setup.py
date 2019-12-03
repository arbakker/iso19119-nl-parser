from setuptools import setup, find_packages

with open('README.md') as f:
    README = f.read()

setup(
    name='service-metadata-converter',
    version='0.1',
    description='PDOK Service Metadata converter',
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
        convert-md=service_md_converter.cli:main
        convert-metadata=service_md_converter.cli:main
    ''',
)
