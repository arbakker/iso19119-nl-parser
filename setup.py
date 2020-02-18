from setuptools import setup, find_packages

version = "0.0.1"

with open('README.md') as f:
    README = f.read()

install_requires = [
    'lxml==4.2.1',
]

tests_require = [
    "pytest",
    "mock",
    "pytest-cov",
    "pytest-flakes",
    "pytest-black",
]

setup(
    name="iso19119-nl-parser",
    version=version,
    description="PDOK service metadata (ISO19119) parser",
    long_description=README,
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=["Programming Language :: Python"],
    keywords=[],
    author="Anton Bakker",
    author_email="anton.bakker@kadaster.nl",
    url="https://github.com/arbakker/iso19119-nl-parser",
    license="MIT",
    packages=["iso19119_nl_parser"],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    entry_points={
        "console_scripts": [
            "parse-md = iso19119_parser.cli:main"
        ]
    },
)
