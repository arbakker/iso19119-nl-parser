import os
from pathlib import Path
from setuptools import setup

version = "0.0.2.dev0"

lib_folder = os.path.dirname(os.path.realpath(__file__))
req_path = os.path.join(lib_folder, "/requirements.txt")
install_requires = []

if os.path.isfile(req_path):
    with open(req_path) as f:
        install_requires = f.read().splitlines()

with open("README.md") as f:
    README = f.read()

install_requires = [
    "lxml==4.2.1",
]

tests_require = [
    "pytest",
    "mock",
    "pytest-cov",
    "pytest-flakes",
    "pytest-black",
]

def get_data_files():
    files = []
    for file_path in Path("iso19139_nl_reader/data").glob("**/*.*"):
        path_string = str(file_path)
        # strip metadata_generator/ from path:
        path_import = os.path.join(*(path_string.split(os.path.sep)[1:]))
        files.append(path_import)
    return  {"iso19139_nl_reader": files}

setup(
    name="iso19139-nl-reader",
    version=version,
    description="PDOK metadata (ISO 19139) parser",
    long_description=README,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=["Programming Language :: Python"],
    keywords=[],
    author="Anton Bakker",
    author_email="anton.bakker@kadaster.nl",
    url="https://github.com/arbakker/iso19139-nl-reader",
    license="MIT",
    packages=["iso19139_nl_reader"],
    package_data=get_data_files(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    entry_points={
        "console_scripts": [
            "read-iso=iso19139_nl_reader.cli:main"
        ]
    },
)
