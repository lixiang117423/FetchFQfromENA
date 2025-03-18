from setuptools import setup, find_packages, find_packages

setup(
    name="fetchFQfromENA",
    version="0.1.4",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'get_fq_meta=fetchFQfromENA.get_fq_meta:main',
            'get_fq_file=fetchFQfromENA.get_fq_file:main'
        ]
    },
    install_requires=[],
    author="Xiang Li",
    author_email="lixiang117423@gmail.com",
    description="Retrieve FASTQ file meta information from ENA and download corresponding data.",
)