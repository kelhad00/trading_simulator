import io
from setuptools import setup, find_packages


setup(
    name = "emotrade",
    version = "0.1.dev1",
    author="Kevin EL HADDAD",
    author_email="kevin.elhaddad@umons.ac.be",
    maintainer="Gatien VILAIN",
    maintainer_email="gatien.vilain@outlook.fr",
    # license="",
    description = (
        "A trading website interface to collect trader actions"
    ),
    keywords = ["Trading", "Interface", "Actions"],
    long_description=io.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url = "https://github.com/kelhad00/trading_simulator",
    project_urls={
        "Source": "https://github.com/kelhad00/trading_simulator",
        "Bug Tracker": "https://github.com/kelhad00/trading_simulator/issues",
    },
    python_requires=">=3.10",
    packages=find_packages(),
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Education",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        # "License :: OSI Approved :: Some License",
        "Operating System :: OS Independent",
    ],
)