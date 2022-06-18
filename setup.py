import sys

from setuptools import find_packages, setup

MIN_PYTHON_VERSION = (3, 7)
CURRENT_PYTHON = sys.version_info[:2]

if CURRENT_PYTHON < MIN_PYTHON_VERSION:
    print(
        f"genome is only supported for Python version is {MIN_PYTHON_VERSION}+."
        f" Detected you are on version {CURRENT_PYTHON}, installation will not proceed!"
    )
    sys.exit(-1)

setup(
    name="lgenome",
    version="v0.0.0",
    author_email="kenny@latch.bio",
    description="A python package to manage curated genomic resources for bioinformatics workflows.",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
