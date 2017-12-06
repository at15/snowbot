import os
import math
import requests
import tarfile
import zipfile
import click

__all__ = ['maybe_download_and_extract', 'convert_size']


def convert_size(size_bytes):
    """
    convert size in bytes to human readable string, i.e. 1024 -> 1KB
    copied from https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
    :param size_bytes:
    :return:
    """
    if size_bytes == 0:
        return '0B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '{} {}'.format(s, size_name[i])


@click.command(name='download')
@click.argument('url')
@click.argument('download_dir')
@click.argument('extract_dir')
def maybe_download_and_extract(url, download_dir, extract_dir=None, silent=False, progress=True):
    def p(*args):
        if not silent:
            print(*args)

    # already extracted
    if extract_dir and os.path.isdir(extract_dir):
        p('found', extract_dir, 'don\'t download from', url)
        return True
    # download file
    file_name = url.split('/')[-1]
    file_path = os.path.join(download_dir, file_name)
    if os.path.exists(file_path):
        p('data has already been downloaded to', file_path)
    else:
        p('downloading', url, 'to', file_path)
        with open(file_path, 'wb') as f:
            res = requests.get(url, stream=True)
            size = res.headers.get('content-length')
            if size and progress:
                size = int(size)
                with click.progressbar(length=size,
                                       label='Downloading {} {}'.format(file_name, convert_size(size))) as bar:
                    for data in res.iter_content(chunk_size=4096):
                        f.write(data)
                        bar.update(len(data))
            else:
                f.write(res.content)  # TODO: don't know if this would work...
    if not extract_dir:
        p('extracted_dir not specified')
        return False
    # TODO: we should separate extract and download
    # extract file
    if file_name.endswith('.zip'):
        zipfile.ZipFile(file=file_path, mode='r').extractall(extract_dir)
    elif file_name.endswith(('.tar.gz', '.tgz')):
        tarfile.open(name=file_path, mode='r:gz').extractall(extract_dir)
    else:
        p('unknown file extension, only support zip, tar.gz but got', file_name)
        return False
    p('file extracted to', extract_dir)
    return True


@click.group()
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(maybe_download_and_extract)
    cli()
