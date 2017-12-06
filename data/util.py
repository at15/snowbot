import os
import requests
import click


@click.command(name='download')
@click.argument('url')
@click.argument('download_dir')
def maybe_download(url, download_dir, extracted_dir='', silent=False, progress=True):
    def p(*args):
        if not silent:
            print(*args)

    if os.path.isdir(extracted_dir):
        p('found', extracted_dir, 'don\'t download from', url)
        return True
    file_name = url.split('/')[-1]
    file_path = os.path.join(download_dir, file_name)
    if os.path.exists(file_path):
        p('data has already been downloaded to', file_path)
    else:
        p('downloading', url, 'to', file_path)
        with open(file_path, 'wb') as f:
            res = requests.get(url, stream=True)
            total_length = res.headers.get('content-length')
            if total_length:
                with click.progressbar(length=int(total_length), label='Downloading ' + file_name) as bar:
                    for data in res.iter_content(chunk_size=4096):
                        f.write(data)
                        bar.update(len(data))


@click.group()
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(maybe_download)
    cli()
