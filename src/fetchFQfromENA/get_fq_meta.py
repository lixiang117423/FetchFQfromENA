import requests
from typing import Optional
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_ENA_API = 'https://www.ebi.ac.uk/ena/portal/api/filereport'
DEFAULT_PARAMS = {
    'result': 'read_run',
    'format': 'tsv',
    'fields': ','.join(sorted({'run_accession', 'study_accession', 'secondary_study_accession', 'sample_accession', 'secondary_sample_accession', 'experiment_accession', 'submission_accession', 'tax_id', 'scientific_name', 'instrument_model', 'nominal_length', 'library_layout', 'library_source', 'library_selection', 'base_count', 'first_public', 'last_updated', 'study_title', 'experiment_alias', 'run_alias', 'fastq_bytes', 'fastq_md5', 'fastq_ftp', 'fastq_aspera', 'fastq_galaxy', 'submitted_bytes', 'submitted_md5', 'submitted_ftp', 'submitted_galaxy', 'submitted_format', 'sra_bytes', 'sra_md5', 'sra_ftp', 'sample_alias', 'broker_name', 'sample_title', 'nominal_sdev', 'bam_ftp', 'bam_bytes'}))
}

def fetch_tsv(
    accession: str,
    output_path: str = './',
    api_url: str = DEFAULT_ENA_API,
    max_retries: int = 3,
    fields: list[str] | None = None
) -> Optional[Path]:
    """Fetch sequencing metadata TSV from ENA API"""
    
    # Handle field selection
    final_fields = DEFAULT_PARAMS.copy()
    if fields:
        if 'all' not in fields:
            final_fields['fields'] = ','.join(sorted({'run_accession'} | set(fields)))
    
    params = {'accession': accession, **final_fields}
    output_path = Path(output_path) if output_path else Path('./')
    default_path = output_path / f'{accession}.meta.tsv'
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        session = requests.Session()
        retries = Retry(total=max_retries, backoff_factor=0.5)
        session.mount('https://', HTTPAdapter(max_retries=retries))

        response = session.get(api_url, params=params, timeout=10)
        response.raise_for_status()

        # process content based on file extensions
        file_content = response.text
        
        if output_path.suffix == '.xlsx':
            import pandas as pd
            import warnings
            warnings.simplefilter('ignore', category=FutureWarning)
            from pandas import DataFrame
            import numpy as np
            
            # Convert TSV to DataFrame with original field order
            df = DataFrame([x.split('\t') for x in file_content.splitlines()])
            df.columns = df.iloc[0]
            df = df[1:]
            
            # Handle empty values and maintain data types
            df.replace('', np.nan, inplace=True)
            
            # Write to Excel with openpyxl engine
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
        else:
            if output_path.suffix == '.csv':
                file_content = file_content.replace('\t', ',')
            
            output_path.write_text(file_content)
        return default_path

    except requests.exceptions.RequestException as e:
        print(f'Failed to download metadata file: {str(e)}')
        return None
    except IOError as e:
        print(f'Failed to save TSV file: {str(e)}')
        return None


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Download sequencing metadata TSV from ENA API'
    )
    parser.add_argument('-id', '--accession',
                        help='ENA accession number (required) (e.g. PRJNA123456)')
    parser.add_argument('-o', '--output', default='./',
                        help='Output path (supports .tsv/.csv/.txt/.xlsx extensions, default: ./[accession].meta.tsv)')
    parser.add_argument('-s', '--save', nargs='+', default=['all'],
                        help='Fields to save (all|field1 field2), available fields: secondary_study_accession,sample_accession,secondary_sample_accession,experiment_accession,study_accession,submission_accession,tax_id,scientific_name,instrument_model,nominal_length,library_layout,library_source,library_selection,base_count,first_public,last_updated,study_title,experiment_alias,run_alias,fastq_bytes,fastq_md5,fastq_ftp,fastq_aspera,fastq_galaxy,submitted_bytes,submitted_md5,submitted_ftp,submitted_galaxy,submitted_format,sra_bytes,sra_md5,sra_ftp,sample_alias,broker_name,sample_title,nominal_sdev,bam_ftp,bam_bytes')
    args = parser.parse_args()
    
    # Validate selected fields
    valid_fields = {'secondary_study_accession','sample_accession','secondary_sample_accession','experiment_accession','study_accession','submission_accession','tax_id','scientific_name','instrument_model','nominal_length','library_layout','library_source','library_selection','base_count','first_public','last_updated','study_title','experiment_alias','run_alias','fastq_bytes','fastq_md5','fastq_ftp','fastq_aspera','fastq_galaxy','submitted_bytes','submitted_md5','submitted_ftp','submitted_galaxy','submitted_format','sra_bytes','sra_md5','sra_ftp','sample_alias','broker_name','sample_title','nominal_sdev','bam_ftp','bam_bytes'}
    
    if 'all' not in args.save and not set(args.save).issubset(valid_fields):
        invalid = set(args.save) - valid_fields
        raise ValueError(f'Invalid fields selected: {invalid}')
    
    result = fetch_tsv(args.accession, args.output, fields=args.save if 'all' not in args.save else None)
    if result:
        print(f'Meta information file saved to: {result}')

if __name__ == '__main__':
    main()