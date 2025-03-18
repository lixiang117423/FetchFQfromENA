from setuptools import setup, find_packages

setup(
    name="fetchFQfromENA",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
    author="Xiang Li",
    author_email="lixiang117423@gmail.com",
    description="Retrieve FASTQ file information from ENA and download corresponding data.",
)