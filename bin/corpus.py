import click

from snowbot.corpus import METAS
from snowbot.corpus.util import maybe_download, maybe_extract


@click.command('download', help='Download and extract corpus to ./data')
@click.argument('name')
def download(name):
    if name not in METAS:
        # TODO: print all we have
        print('unknown corpus', name, 'use list command to see all supported')
        return
    # TODO: real download logic


@click.command('list', help='Show known Corpus that can be downloaded')
def lst():
    print('Name\t Description\tURL')
    for name, m in METAS.items():
        print(name, m['full_name'], m['url'])


# TODO: maybe_download does not handle nor return error
@click.command(name='download_file', help='Download file to folder, like wget/curl')
@click.argument('url')
@click.argument('download_dir')
def download_file(url, download_dir):
    maybe_download(url, download_dir)


# TODO: not tested
@click.command(name='extract_file', help='Extract .zip/tar.gz to folder, like tar w/o -zxvf')
@click.argument('file')
@click.argument('folder')
def extract_file(file, folder):
    if maybe_extract(file, folder):
        print(file, 'extracted to', folder, 'or already exists')
    else:
        print('failed to extract', file, 'to', folder)


@click.group()
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(download)
    cli.add_command(lst)
    cli.add_command(download_file)
    cli.add_command(extract_file)
    cli()
