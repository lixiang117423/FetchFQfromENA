# FetchFQfromENA

A Python tool to fetch FASTQ files from ENA database

## Installation
```bash
pip install -r requirements.txt
python setup.py install
```

## Usage Example
```python
from fetchFQfromENA import download_fastq

download_fastq(accession='ERR000000', output_dir='./data')
```

## Features
- Multi-threaded downloads
- Automatic file integrity verification
- ENA metadata query support

## Requirements
- Python 3.7+
- requests>=2.31.0