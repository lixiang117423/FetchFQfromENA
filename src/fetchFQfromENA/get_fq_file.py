import os
import hashlib
from concurrent.futures import ThreadPoolExecutor
from typing import List, Union
import requests
from pathlib import Path
from fetchFQfromENA.get_fq_meta import fetch_tsv  # Metadata fetching function
import argparse
from typing import Tuple


def parse_args() -> Tuple[str, str, str, str, str]:
    parser = argparse.ArgumentParser(
    description='Download FASTQ files from ENA',
    add_help=True,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
    parser.add_argument('--accession', '-id', required=True,
                    help='Accession number (required)\nFormat example: PRJNA661210/SRP000123\nSupports ENA/NCBI standard accession formats')
    parser.add_argument('--type', '-t', choices=['ftp', 'aspera'], required=True,
                      help='Download protocol type\nftp: Standard FTP download\naspera: High-speed transfer protocol (requires private key)')
    parser.add_argument('--key', '-k',
                    help='Path to aspera private key\nRequired when using aspera protocol\nDefault location: ~/.aspera/connect/etc/asperaweb_id_dsa.openssh')
    parser.add_argument('--method', '-m', choices=['run', 'save'], default='save',
                     help='Execution mode\nrun: Execute download commands directly\nsave: Generate download script (default)')
    parser.add_argument('--output', '-o',
                    help='Output directory\nDefault format: [accession].fastq.download\nAuto-create missing directories')
    args = parser.parse_args()

    if args.type == 'aspera':
        if not args.key:
            parser.error('--key is required when using aspera protocol')
        key_file = Path(args.key)
        if not key_file.exists():
            parser.error(f'Aspera key file {key_file} does not exist')
        if key_file.stat().st_mode & 0o777 != 0o600:
            parser.error(f'Key file permissions are insecure (current: {oct(key_file.stat().st_mode & 0o777)}).\nRun: chmod 600 "{key_file}" to fix')

    output_dir = args.output or f"{args.accession}.fastq.download"
    return args.accession, args.type, args.key, output_dir, args.method

def build_download_command(link: str, protocol: str, output_dir: str, key_path: str = None) -> str:
    if protocol == 'ftp':
        return f'wget -c {link} -P {output_dir}'
    elif protocol == 'aspera' and key_path:
        return f'ascp -v -k 1 -T -l 1000m -P 33001 -i {key_path} era-fasp@{link} {output_dir}/'

def process_metadata(accession: str, protocol: str) -> List[str]:
    meta_file = f'.{accession}.meta.txt'
    
    try:
        with open(meta_file, 'r') as f:
            header = f.readline().strip().split('\t')
            column_index = header.index('fastq_aspera' if protocol == 'aspera' else 'fastq_ftp')
            
            return [
    link.strip()
    for line in f
    if line.strip()
    for link in line.strip().split('\t')[column_index].split(';')
    if link.strip()
]
    except FileNotFoundError:
        print(f'Metadata file {meta_file} not found')
        return []


def main():
    accession, protocol, key_path, output_dir, method = parse_args()
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Fetch metadata file
    fetch_tsv(accession, output_path=f'.{accession}.meta.txt')
    
    # Process metadata
    download_links = process_metadata(accession, protocol)
    
    # Build download commands
    commands = [
        build_download_command(link, protocol, output_dir, key_path)
        for link in download_links
    ]

    if method == 'save':
        # Write commands to shell script
        # script_path = Path(f'./download_{accession}_fastq_by_{protocol}.sh')

        if protocol == 'aspera':
            script_path = Path(f'./download_{accession}_fastq_by_{protocol}.sh')
        else:
            script_path = Path(f'./download_{accession}_fastq_by_wget.sh')


        with script_path.open('w', newline='\n') as f:
            f.write('#!/bin/bash\n')
            f.write('\n'.join(filter(None, commands)))
        
        script_path.chmod(0o755)
        print(f'\n\033[32mDownload script generated: {script_path.resolve()}\033[0m')
        print('Please run next command to download the FASTQ data:\n' + ' '.join(['bash', str(script_path)]))
    else:
        # Execute commands sequentially
        print(f'\n\033[33mStarting direct download with {len(commands)} files\033[0m')
        for i, cmd in enumerate(filter(None, commands), 1):
            print(f'Downloading file {i}/{len(commands)}')
            try:
                os.system(cmd)
            except Exception as e:
                print(f'\033[31mError downloading: {e}\033[0m')

if __name__ == '__main__':
    main()