import os
from snowbot.corpus.util import maybe_download, maybe_extract


class TwitterDataSet:
    NAME = 'twitter'
    FULL_NAME = 'Marsan-Ma/chat_corpus twitter_en'
    URL = 'https://github.com/Marsan-Ma/chat_corpus'
    DATA_URL = 'https://raw.githubusercontent.com/Marsan-Ma/chat_corpus/master/twitter_en.txt.gz'
    FILES = [
        'twitter_en.txt'
    ]

    def __init__(self, home):
        self.tmp = '/tmp'
        self.home = home

    def download_and_extract(self):
        extract_dst = self.home
        if os.path.exists(extract_dst):
            print('extracted twitter data already exists')
            return
        file = maybe_download(self.DATA_URL, download_dir=self.tmp)
        maybe_extract(file, extract_dst)
