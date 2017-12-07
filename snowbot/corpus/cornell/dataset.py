import os
import shutil

from snowbot.corpus.util import maybe_download, maybe_extract

NAME = 'cornell'
FULL_NAME = 'Cornell Movie Dialog Corpus'
URL = 'https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html'
DATA_URL = 'http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip'

_SEP = '+++$+++'


def download(dst, tmp):
    if os.path.exists(dst):
        print('extracted cornell data already exist')
        return
    file = maybe_download(DATA_URL, download_dir=tmp)
    extract_to = os.path.join(tmp, 'cornell-tmp')
    maybe_extract(file, extract_to)
    shutil.move(extract_to + '/cornell movie-dialogs corpus', dst)
    shutil.rmtree(extract_to, ignore_errors=True)
