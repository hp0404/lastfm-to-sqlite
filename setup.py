from setuptools import setup, find_packages
import os

VERSION = "0.2.3"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="lastfm-to-sqlite",
    description="Scrape LAST.FM playlists to SQLite",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/hp0404/lastfm-to-sqlite",
    project_urls={
        "Documentation": "https://lastfm.readthedocs.io/en/latest/",
        "Issues": "https://github.com/hp0404/lastfm-to-sqlite/issues",
        "Changelog": "https://github.com/hp0404/lastfm-to-sqlite/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=find_packages(exclude=["tests", "tests.*"]),
    entry_points={"console_scripts": ["lastfm=lastfm.cli:cli"]},
    install_requires=["requests", "sqlite-utils"],
    extras_require={
        "test": ["pytest"],
        "docs": ["sphinx", "sphinx-rtd-theme"]
    },
    tests_require=["lastfm[test]"],
    python_requires=">=3.6",
)
