# FetchFQfromENA

A Python tool to fetch FASTQ files from ENA database

## Installation
```bash
pip install fetchfqfromena
```

## Usage Example

### get the meta information of a project or run

```bash
get_fq_meta -h

usage: get_fq_meta [-h] [-id ACCESSION] [-o OUTPUT] [-s SAVE [SAVE ...]]

Download sequencing metadata TSV from ENA API

options:
  -h, --help            show this help message and exit
  -id ACCESSION, --accession ACCESSION
                        ENA accession number (required) (e.g. PRJNA123456)
  -o OUTPUT, --output OUTPUT
                        Output path (supports .tsv/.csv/.txt/.xlsx extensions, default: ./tmp/[accession].meta.tsv)
  -s SAVE [SAVE ...], --save SAVE [SAVE ...]
                        Fields to save (all|field1 field2), available fields: secondary_study_accession,sample_accession,secondary_sample_acces  
                        sion,experiment_accession,study_accession,submission_accession,tax_id,scientific_name,instrument_model,nominal_length,l  
                        ibrary_layout,library_source,library_selection,base_count,first_public,last_updated,study_title,experiment_alias,run_al  
                        ias,fastq_bytes,fastq_md5,fastq_ftp,fastq_aspera,fastq_galaxy,submitted_bytes,submitted_md5,submitted_ftp,submitted_gal  
                        axy,submitted_format,sra_bytes,sra_md5,sra_ftp,sample_alias,broker_name,sample_title,nominal_sdev,bam_ftp,bam_bytes 
```

```
get_fq_meta -id PRJNA510920 -o /mnt/d/OneDrive/NAS/PRJNA510920.meta.txt
# TSV file saved to: /mnt/d/OneDrive/NAS/PRJNA510920.meta.txt/PRJNA510920.meta.tsv
```

### download FASTQ format data from ENA

```bash
get_fq_file -h

usage: get_fq_file [-h] --accession ACCESSION --type {ftp,aspera} [--key KEY] [--method {run,save}] [--output OUTPUT]

Download FASTQ files from ENA

options:
  -h, --help            show this help message and exit
  --accession ACCESSION, -id ACCESSION
                        Accession number (required) Format example: PRJNA661210/SRP000123 Supports ENA/NCBI standard accession formats
                        (default: None)
  --type {ftp,aspera}, -t {ftp,aspera}
                        Download protocol type ftp: Standard FTP download aspera: High-speed transfer protocol (requires private key) (default:  
                        None)
  --key KEY, -k KEY     Path to aspera private key Required when using aspera protocol Default location:
                        ~/.aspera/connect/etc/asperaweb_id_dsa.openssh (default: None)
  --method {run,save}, -m {run,save}
                        Execution mode run: Execute download commands directly save: Generate download script (default) (default: save)
  --output OUTPUT, -o OUTPUT
                        Output directory Default format: [accession].fastq.download Auto-create missing directories (default: None)
```

`-m run` will directly download the FASTQ files.  **But we strongly recommend using ` -m save` to save download script then get the FASTQ data.**

#### wget

```bash
get_fq_file -id PRJNA510920 -m save -t ftp -o /mnt/d/OneDrive/NAS

Download script generated: /mnt/d/OneDrive/NAS/02.编程相关/FetchFQfromENA/download_PRJNA510920_fastq_by_wget.sh
Please run next command to download the FASTQ data:
bash download_PRJNA510920_fastq_by_wget.sh
```

#### aspera

```bash
get_fq_file -id PRJNA510920 -m save -t aspera -k ~/miniforge3/etc/asperaweb_id_dsa.openssh  -o /mnt/d/OneDrive/NAS

Download script generated: /mnt/d/OneDrive/NAS/02.编程相关/FetchFQfromENA/download_PRJNA510920_fastq_by_aspera.sh
Please run command to download the FASTQ data:
bash download_PRJNA510920_fastq_by_aspera.sh
```


## Requirements
- Python 3.7+
- requests>=2.31.0