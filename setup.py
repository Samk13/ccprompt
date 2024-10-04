# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Sam Arbid.
#
# CCprompt is free software, you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file details.

from setuptools import setup, find_packages
from ccprompt import __version__

setup(
    name="ccprompt",
    version=f"{__version__}",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "ccprompt=ccprompt.main:main",
        ],
    },
    author="Sam Arbid",
    author_email="samarbid13@gmail.com",
    description="Extract code context for AI prompts based on a function or class name.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Samk13/ccprompt",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        # No required dependencies
    ],
    extras_require={
        "javascript": ["esprima"],
        "dev": ["ruff"],
    },
    python_requires=">=3.9",
)
