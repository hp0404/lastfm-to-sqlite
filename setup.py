from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="lastfm",
    description="Scrape LAST.FM playlists to SQLite",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/hp0404/lastfm",
    project_urls={
        "Issues": "https://github.com/hp0404/lastfm/issues",
        "CI": "https://github.com/hp0404/lastfm/actions",
        "Changelog": "https://github.com/hp0404/lastfm/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["lastfm"],
    install_requires=[],
    extras_require={
        "test": ["pytest"],
        "docs": ["sphinx", "sphinx-rtd-theme"]
    },
    tests_require=["lastfm[test]"],
    python_requires=">=3.6",
)
