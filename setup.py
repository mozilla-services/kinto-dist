import codecs
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read_file(filename):
    """Open a related file and return its content."""
    with codecs.open(os.path.join(here, filename), encoding="utf-8") as f:
        content = f.read()
    return content


README = read_file("README.rst")
CHANGELOG = read_file("CHANGELOG.rst")

INSTALL_REQUIRES = [
    x.replace(" \\", "")
    for x in read_file("./requirements.txt").split("\n")
    if not x.startswith(" ")
]

setup(
    name="kinto-dist",
    version="27.0.0",
    description="Kinto Distribution",
    long_description=README + "\n\n" + CHANGELOG,
    license="Apache License (2.0)",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords="web services",
    author="Mozilla Services",
    author_email="services-dev@mozilla.com",
    url="https://github.com/mozilla-services/kinto-dist",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=INSTALL_REQUIRES,
)
