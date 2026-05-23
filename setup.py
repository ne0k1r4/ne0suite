from setuptools import setup, find_packages

setup(
    name="ne0suite",
    version="1.0.0",
    description="Unified Operator CLI — GRIMOIRE · LightScan · WRAITH-NET",
    author="Light",
    author_email="neok1ra@proton.me",
    url="https://github.com/ne0k1r4/ne0suite",
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "ne0suite=ne0suite.cli:main",
            "n0s=ne0suite.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
        "Environment :: Console",
    ],
)
