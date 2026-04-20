import argparse
import os
from pathlib import Path
import zipfile
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import requests

zenodo_id = 19427673
zenodo_file = 'FeMo_TCP_dataset.zip'
zenodo_description = 'ZENODO_DESCRIPTION.md'

root_path = os.path.dirname(os.path.dirname(__file__))


def mode_str(file):
    if file.endswith('.zip'):
        return 'wb'
    elif file.endswith('.md'):
        return 'w'

def file_url(thefile):
    return f'https://zenodo.org/record/{zenodo_id}/files/{thefile}'

def main():

    assert os.path.exists(os.path.join(root_path, 'README.md'))

    logging.info('Downloading https://zenodo.org/records/19427673')

    for file in [ zenodo_description,  zenodo_file ]:
        this_full_url = file_url(file)
        logging.info(f'Downloading { file } from {this_full_url}')
        destination = os.path.join(root_path, file)
        response = requests.get(this_full_url, stream=True, timeout=120)
        response.raise_for_status()

        file_mode = mode_str(file)
        logging.info(f'writing to disk') # with mode  { file_mode } ')
        
        with open(destination, 'wb' ) as  file_handle:
            for chunk in response.iter_content(chunk_size=1024*64):
                if chunk:
                    file_handle.write(response.content)


    assert os.path.exists(zenodo_file)
    assert os.path.exises(zenodo_description)

    logging.info(f'finished downloading from zenodo')

    with zipfile.ZipFile(zenodo_file, 'r') as zip_ref:
        zip_ref.extractall(root_path)



if __name__ == '__main__':
    main()
