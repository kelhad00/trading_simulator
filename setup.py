import io
from setuptools import setup, find_packages


setup(
    # Check https://setuptools.pypa.io/en/latest/references/keywords.html for a full list of keywords
    name = "emotrade",
    version = "0.2.0",
    description = (
        "A stock market site simulator for collecting data on stocks carried out by the trader."
    ),
    long_description=io.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Kevin EL HADDAD",
    author_email="kevin.elhaddad@umons.ac.be",
    maintainer="Gatien VILAIN",
    maintainer_email="gatien.vilain@outlook.fr",
    url = "https://github.com/kelhad00/trading_simulator",
    # download_url =
    packages=find_packages(),
    scripts=["bin/emotrade"], # "Provide command-line scripts for the user to run"
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Education",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    # license="",
    # license_files = ("LICENSE.txt",),
    keywords = ["Trading", "Interface", "Actions"],
    package_data={"emotrade": ["assets/*", "Setup/*.ipynb"]},
    install_requires=[
        'dash ==2.10.2',
        'pandas ==2.0.2',
    ],
    extras_require={
        'extra': [
            'yahooquery ==2.3.1',
            'notebook'
        ],
    },
    python_requires="==3.10.*",
    project_urls={
        "Source": "https://github.com/kelhad00/trading_simulator",
        "Bug Tracker": "https://github.com/kelhad00/trading_simulator/issues",
    },
)