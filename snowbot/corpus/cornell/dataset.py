import os
import shutil

from snowbot.corpus.util import maybe_download, maybe_extract

_SEP = '+++$+++'


class CornellDataSet:
    NAME = 'cornell'
    FULL_NAME = 'Cornell Movie Dialog Corpus'
    URL = 'https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html'
    DATA_URL = 'http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip'

    def __init__(self):
        self.tmp = '/tmp'

    def download_and_extract(self, extract_dst):
        if os.path.exists(extract_dst):
            print('extracted cornell data already exist')
            return
        file = maybe_download(self.DATA_URL, download_dir=self.tmp)
        extract_to = os.path.join(self.tmp, 'cornell-tmp')
        maybe_extract(file, extract_to)
        shutil.move(extract_to + '/cornell movie-dialogs corpus', extract_dst)
        print('remove', extract_to)
        shutil.rmtree(extract_to, ignore_errors=True)
