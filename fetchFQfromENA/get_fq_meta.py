import argparse
import sys
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import csv
import pandas as pd

def fetch_tsv(accession, output_file=None):
    base_url = f"https://www.ebi.ac.uk/ena/portal/api/filereport?accession={accession}&result=read_run"
    
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1)
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(base_url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    if not output_file:
        output_file = Path.cwd() / f"{accession}_ENA.meta.txt"
    else:
        output_file = Path(output_file)

    output_file.parent.mkdir(parents=True, exist_ok=True)

    suffix = output_file.suffix.lower()
    
    if suffix == '.xlsx':
        df = pd.read_csv(response.text, sep='\t')
        df.to_excel(output_file, index=False)
    elif suffix == '.csv':
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv.reader(response.text.splitlines(), delimiter='\t'))
    else:  # Default to TSV/txt
        with open(output_file, 'w') as f:
            f.write(response.text)
    
    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch FASTQ metadata from ENA')
    parser.add_argument('accession', help='ENA study/project accession number')
    parser.add_argument('-o', '--output', help='Output file path (supports .tsv, .csv, .xlsx)')
    args = parser.parse_args()
    
    result = fetch_tsv(args.accession, args.output)
    if result:
        print(f"Metadata saved to: {result}")
    else:
        print("Failed to fetch metadata")
        sys.exit(1)