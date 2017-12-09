import os
import re
from snowbot.corpus.util import maybe_download, maybe_extract, files_exist, files_missing, train_test_split


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

    def convert(self):
        if not files_exist(self.home, self.FILES):
            print('following files are missing', files_missing(self.home, self.FILES))
            return False
        print('nothing to convert, you are all set')
        return True

    def gen_qa(self, q='q.txt', a='a.txt'):
        questions = []
        answers = []
        with open(os.path.join(self.home, 'twitter_en.txt'), 'r') as f:
            is_q = True
            for l in f:
                if is_q:
                    questions.append(l)
                    is_q = False
                else:
                    answers.append(l)
                    is_q = True
        assert len(questions) == len(answers)
        print('total', len(questions), 'qa')
        q, a = os.path.join(self.home, q), os.path.join(self.home, a)
        with open(q, 'w') as f:
            f.write('\n'.join(questions))
        with open(a, 'w') as f:
            f.write('\n'.join(answers))
        return True

    # FIXME: the split, _split, remove_stupid, is_stupid are all copied from cornell dataset
    def split(self, q='q.txt', a='a.txt', remove_stupid=True):
        with open(os.path.join(self.home, q), 'r') as f:
            questions = f.read().splitlines()
        with open(os.path.join(self.home, a), 'r') as f:
            answers = f.read().splitlines()
        if remove_stupid:
            questions, answers = remove_stupid_qa(questions, answers)
        return self._split(questions, answers)

    def _split(self, questions, answers):
        d = train_test_split(questions, answers, 0.1)
        m = {
            'src-train.txt': 'train_enc',
            'tgt-train.txt': 'train_dec',
            'src-val.txt': 'test_enc',
            'tgt-val.txt': 'test_dec'
        }
        for dst, src in m.items():
            p = os.path.join(self.home, dst)
            print('write', src, 'to', p)
            with open(p, 'w') as f:
                f.write('\n'.join(d[src]))
        return True


def remove_stupid_qa(questions, answers):
    assert len(questions) == len(answers)
    cleaner = re.compile('(<u>|</u>|\[|\])')
    q_clever = []
    a_clever = []
    n_stupid = 0
    for i in range(len(questions)):
        q = cleaner.sub('', questions[i]).lower()
        a = cleaner.sub('', answers[i]).lower()
        if is_stupid(q) or is_stupid(a):
            n_stupid += 1
            continue
        q_clever.append(q)
        a_clever.append(a)
    assert len(q_clever) == len(a_clever)
    print('n_stupid', n_stupid)
    return q_clever, a_clever


def is_stupid(line):
    if len(line) < 15 and ('don\'t' in line) and ('know' in line):
        return True
    if len(line) < 5:
        if ('yeah' in line) or ('yes' in line) or ('no' in line):
            return True
    return False
