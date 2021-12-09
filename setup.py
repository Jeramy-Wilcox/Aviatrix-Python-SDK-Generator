#!/usr/bin/env python
"""The setup script."""
from setuptools import find_packages, setup

__version__ = "0.1.0"
__author__ = "Jeramy Wilcox"

with open("README.md", "r", encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    INSTALL_REQUIRES = f.read().splitlines()

setup(
    name="aviatrix-sdk-generator",
    version=__version__,
    author=__author__,
    author_email="jeramy.wilcox3@gmail.com",
    description="Generates a python library to interact with the Aviatrix API.",
    long_description=readme,
    keywords="aviatrix sdk automation network infrastructure cloud",
    license="MIT",
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.8",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "console_scripts": [
            "generate-aviatrix-sdk=aviatrix_sdk_generator.generate:cli",
        ],
    },
    data_files=[
        (
            "aviatrix_sdk_templates",
            [
                "aviatrix_sdk_generator/aviatrix_sdk_templates/__init__.j2",
                "aviatrix_sdk_generator/aviatrix_sdk_templates/api_base.j2",
                "aviatrix_sdk_generator/aviatrix_sdk_templates/class.j2",
                "aviatrix_sdk_generator/aviatrix_sdk_templates/client.j2",
                "aviatrix_sdk_generator/aviatrix_sdk_templates/exceptions.j2",
                "aviatrix_sdk_generator/aviatrix_sdk_templates/func.j2",
                "aviatrix_sdk_generator/aviatrix_sdk_templates/property.j2",
                "aviatrix_sdk_generator/aviatrix_sdk_templates/response.j2",
            ],
        )
    ],
)
