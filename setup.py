#!/usr/bin/env python3
"""
Setup script for weex-cli
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="weex-cli",
    version="1.0.0",
    author="SignalAlpha",
    description="WEEX合约交易命令行工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/signalalpha/weex-cli",
    py_modules=["weex_cli"],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "weex-cli=weex_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
)
