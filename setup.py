from setuptools import setup, find_packages

setup(
    name="ne0suite",
    version="0.0.1",
    description="Unified Operator CLI — one entry point for the toolchain",
    author="Light",
    author_email="neok1ra@proton.me",
    url="https://github.com/ne0k1r4/ne0suite",
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "ne0suite=ne0suite.cli:main",
            "n0s=ne0suite.cli:main",
            "ne0=ne0suite.cli:main",
        ],
    },
)
