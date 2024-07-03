import io
from setuptools import setup, find_packages


setup(
    # Check https://setuptools.pypa.io/en/latest/references/keywords.html for a full list of keywords
    name = "tradesim",
    version = "0.2.2",
    description = (
        "A stock market site simulator for collecting data on stocks carried out by the trader."
    ),
    long_description=io.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Gatien VILAIN, Capucine FOUILLARD, Paul HERBEAU, Kevin EL HADDAD",
    author_email="kevin.elhaddad@umons.ac.be, gatien.vilain@outlook.fr, capucine.fouillard@student.junia.com, paul.herbeau01@gmail.com",
    url = "https://github.com/kelhad00/trading_simulator",
    download_url = "https://github.com/kelhad00/trading_simulator/releases",
    packages=find_packages(),
    scripts=["bin/tradesim"], # "Provide command-line scripts for the user to run"
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Dash",
        "Framework :: Flask",
        "Intended Audience :: Education",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        'License :: OSI Approved :: Apache Software License',
        "Topic :: Scientific/Engineering",
    ],
    license='Apache 2.0',
    license_files = ("LICENSE",),
    package_data={"tradesim": ["assets/*", "Setup/*.ipynb"]},
    install_requires=[
        'trade ==2.10.2',
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