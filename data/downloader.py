#!/usr/bin/env python3

import os
import shutil
import click

from .util import maybe_extract, maybe_download
from .cornell import NAME as C_NAME, DATA_URL as C_DURL


@click.command()
@click.argument('dataset')
def cli(dataset):
    dataset = dataset.lower()
    if dataset == C_NAME:
        # TODO: maybe add a force remove folder
        dst = 'raw/cornell'
        if os.path.exists(dst):
            print('extracted cornell data already exist')
            return
        file = maybe_download(C_DURL, download_dir='raw')
        maybe_extract(file, 'cornell-tmp')
        shutil.move('cornell-tmp/cornell movie-dialogs corpus', dst)
        shutil.rmtree('cornell-tmp', ignore_errors=True)
    else:
        print('unknown dataset', dataset)
    print('finish download and extract', dataset, 'dataset')


if __name__ == '__main__':
    cli()
