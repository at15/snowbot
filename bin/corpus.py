import os
import click

from snowbot.corpus import CORPUS
from snowbot.corpus.util import maybe_download, maybe_extract


def corpus_must_exists(name):
    if name not in CORPUS:
        print('unknown corpus', name, 'following is all supported')
        print_corpus()
        exit(1)


def print_corpus():
    print('Name\t Description\tURL')
    for name, m in CORPUS.items():
        print(name, m.NAME, m.URL)


@click.command('list', help='Show known Corpus that can be downloaded')
def lst():
    print_corpus()


@click.command('download', help='Download and extract corpus to ./data')
@click.argument('name')
def download(name):
    corpus_must_exists(name)
    extract_folder = 'data/' + name
    if os.path.exists(extract_folder):
        print('extracted data already exist in', extract_folder)
        return
    corpus = CORPUS[name](home=extract_folder)
    corpus.download_and_extract(extract_folder)


@click.command('convert', help='Convert raw data to format like csv')
@click.argument('name')
def convert(name):
    corpus_must_exists(name)
    corpus = CORPUS[name](home='data/' + name)
    corpus.convert()


@click.command('gen_qa', help='generate one turn dialog (QA)')
@click.argument('name')
def gen_qa(name):
    corpus_must_exists(name)
    corpus = CORPUS[name](home='data/' + name)
    corpus.gen_qa()


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
    cli.add_command(lst)
    cli.add_command(download)
    cli.add_command(convert)
    cli.add_command(gen_qa)
    cli.add_command(download_file)
    cli.add_command(extract_file)
    cli()
