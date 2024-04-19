from glob import glob
import os
import yaml


def get_config(config_path='./config.yaml'):
    with open(config_path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def get_samples():
    fastq_paths = glob('./fastq/*.fastq.gz')
    return fastq_paths


def run_mirge(config, operating_system='mac'):
    if operating_system == 'mac':
        os_str = 'macos'
    elif operating_system == 'linux':
        os_str = 'linux'
    samples = get_samples()
    samples_str = ','.join(samples)

    output_folder = config['output_folder']
    bowtie_path = config['bowtie_path']
    samtools_path = config['samtools_path']
    output_bam: bool = config['bam_output']
    bam_str = '-bam' if output_bam else ''
    min_length = config['min_length']
    species = config['species']
    n_cpus = config['n_cpus']

    install = config['install_tools']

    if install:
        # Get rnafold
        os.chdir('mirge_library')
        os.system("wget -O rnafold.tar.gz https://www.tbi.univie.ac.at/RNA/download/sourcecode/2_4_x/ViennaRNA-2.4.16.tar.gz")
        os.system("tar -xvf rnafold.tar.gz")
        os.chdir('..')

        # Get bowtie
        os.chdir('mirge_library')
        os.system(f"wget -O bowtie-1.3.0-{os_str}-x86_64.zip https://sourceforge.net/projects/bowtie-bio/files/bowtie/1.3.0/bowtie-1.3.0-{os_str}-x86_64.zip/download")
        os.system(f"unzip bowtie-1.3.0-{os_str}-x86_64.zip")
        os.chdir('..')


        # Get samtools
        os.chdir('./mirge_library')
        if operating_system == 'mac':
            os.system('brew install samtools')
        elif operating_system == 'linux':
            os.sysconf('sudo apt-get install samtools')
        else:
            print('Sorry windows users...')
            raise RuntimeError('Operating system not supported')
        os.chdir('..')

        # Get species specific library
        library_download_str = f'\
            wget \
            -O {species}.tar.gz \
            "https://sourceforge.net/projects/mirge3/files/miRge3_Lib/{species}.tar.gz/download"\
        '
        if not os.path.exists('mirge_library/{species}'):
            os.chdir('mirge_library')
            print('Downloading library...')
            os.system(library_download_str)
            print('Extracting library...')
            os.system(f'tar -xvf {species}.tar.gz')
            os.chdir('..')

    mirge_run_string = f'\
        mirge3.0 \
        -s {samples_str} \
        -o {output_folder} \
        -pbwt {bowtie_path} \
        -psam {samtools_path} \
        -prf ./mirge_library/ViennaRNA-2.4.16 \
        -m {min_length} \
        {bam_str} \
        -cpu {n_cpus} \
        -lib mirge_library \
        -db miRBase \
        -on {species} \
        -a illumina \
        '
    
    print('running mirge...')
    os.system(mirge_run_string)
    print('finished!')

if __name__ == '__main__':
    config = get_config()
    run_mirge(config)