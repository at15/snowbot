import os
import re
import shutil
import json
import pandas as pd

from snowbot.corpus.util import maybe_download, maybe_extract, files_exist, files_missing, train_test_split, \
    base_vocab_dict

_SEP = '+++$+++'


class CornellDataSet:
    NAME = 'cornell'
    FULL_NAME = 'Cornell Movie Dialog Corpus'
    URL = 'https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html'
    DATA_URL = 'http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip'
    FILES = [
        'movie_titles_metadata.txt',
        'movie_characters_metadata.txt',
        'movie_lines.txt',
        'movie_conversations.txt'
    ]

    def __init__(self, home):
        self.tmp = '/tmp'
        self.home = home

    def download_and_extract(self):
        extract_dst = self.home
        if os.path.exists(extract_dst):
            print('extracted cornell data already exist')
            return
        file = maybe_download(self.DATA_URL, download_dir=self.tmp)
        extract_to = os.path.join(self.tmp, 'cornell-tmp')
        maybe_extract(file, extract_to)
        shutil.move(extract_to + '/cornell movie-dialogs corpus', extract_dst)
        print('remove', extract_to)
        shutil.rmtree(extract_to, ignore_errors=True)

    def convert(self):
        if not files_exist(self.home, self.FILES):
            print('following files are missing', files_missing(self.home, self.FILES))
            return False
        files = {
            'movie_titles_metadata': {
                'cols': ['id', 'title', 'year', 'imdb_rating', 'imdb_votes', 'genres'],
                'array_col': 5,
                'escape_col': 1
            },
            'movie_characters_metadata': {
                'cols': ['id', 'name', 'movie_id', 'movie_title', 'gender', 'position_in_credits'],
                'escape_col': 3
            },
            'movie_lines': {
                'cols': ['id', 'character_id', 'movie_id', 'character_name', 'utterance'],
                'escape_col': 4
            },
            'movie_conversations': {
                'cols': ['character_id_1', 'character_id_2', 'movie_id', 'lines'],
                'array_col': 3
            }
        }
        for f, m in files.items():
            array_col, escape_col = m.get('array_col', -1), m.get('escape_col', -1)
            text2csv(os.path.join(self.home, f + '.txt'), os.path.join(self.home, f + '.csv'),
                     m['cols'], array_col, escape_col)
        return True

    def gen_qa(self, q='q.txt', a='a.txt'):
        conversations = get_conversations(os.path.join(self.home, 'movie_conversations.csv'))
        id2line = get_id2line(os.path.join(self.home, 'movie_lines.csv'))
        questions, answers, n_empty = [], [], 0
        for conv in conversations:
            for i in range(len(conv) - 1):
                if not id2line[conv[i]] or not id2line[conv[i + 1]]:
                    n_empty += 1
                    continue
                questions.append(id2line[conv[i]])
                answers.append(id2line[conv[i + 1]])
        if len(questions) != len(answers):
            print('got {} questions but {} answers'.format(len(questions), len(answers)))
            return False
        print('total {} conversations, transformed to {} qa, skipped {} empty'.format(
            len(conversations), len(questions), n_empty))
        q, a = os.path.join(self.home, q), os.path.join(self.home, a)
        print('save questions and answers to', q, a)
        count_stupid_lines(questions)
        count_stupid_lines(answers)
        with open(q, 'w') as f:
            f.write('\n'.join(questions))
        with open(a, 'w') as f:
            f.write('\n'.join(answers))
        # TODO: allow split when gen qa?
        return True

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

    def gen_vocab(self):
        # only use train data to generate vocab
        gen_vocab(
            os.path.join(self.home, 'src-train.txt'),
            os.path.join(self.home, 'src-vocab.json')
        )
        gen_vocab(
            os.path.join(self.home, 'tgt-train.txt'),
            os.path.join(self.home, 'tgt-vocab.json')
        )


def text2csv(src, dst, columns, array_col=-1, escape_col=-1):
    """Convert the original Cornell Movie Dialog corpus to csv because pandas can't load it directly

    The original text is separated by +++$+++, when using pandas, it is treated as regular expression,
    and pandas will switch to python engine and fail. Also it contains comma because certain fields like
    genres and lines are array ['L102', 'L103'].

    After conversion, it becomes a csv, and array is converted to 'L102','L103'. Space are trimmed,
    quote is added for escape_col, only movie_lines.txt has string that need to be quoted.

    NOTE: it can result in empty string, which will be treated as NaN in pandas, use df = df.fillna('') to solve it.
    see #9 https://github.com/at15/snowbot/issues/9

    :param src: str
    :param dst: str
    :param columns: list
    :param array_col: int
    :param escape_col: int
    :return:
    """
    print('convert', src, 'to', dst)
    n_cols = len(columns)
    lines = []
    with open(src, 'r', errors='ignore') as f:
        i = 0
        for l in f:
            i += 1
            cells = l.split(_SEP)
            if n_cols != len(cells):
                print(src)
                print('n_cols and cells does not match {} != {}', n_cols, len(cells))
            clean_cells = []
            for i in range(n_cols):
                c = cells[i].strip()
                if array_col == i:
                    c = c.replace(',', ';')[1:-1]  # ['1','2'] -> '1';'2'
                if escape_col == i:
                    c = '"' + c.replace('"', '""') + '"'
                clean_cells.append(c)
            lines.append(','.join(clean_cells) + '\n')
    with open(dst, 'w') as f:
        f.write(','.join(columns) + '\n')
        for l in lines:
            f.write(l)


def get_conversations(movie_conversations_csv):
    df = pd.read_csv(movie_conversations_csv)
    conversations = []
    for conversation in df['lines']:
        # str 'L1'; 'L2' -> list [L1, L2]
        conversations.append([l.strip()[1:-1] for l in conversation.split(';')])
    return conversations


def get_id2line(movie_lines_csv):
    df = pd.read_csv(movie_lines_csv)
    # NOTE: pandas treat empty string column as NaN, which is float, cause error when ','.join(lines)
    df = df.fillna('')
    id2line = {}
    for line_id, line in zip(df['id'], df['utterance']):
        id2line[line_id] = line
    return id2line


def count_stupid_lines(lines):
    cleaner = re.compile('(<u>|</u>|\[|\])')
    n_idk = 0
    n_yeah = 0
    n_no = 0
    for raw in lines:
        cleaned = cleaner.sub('', raw).lower()
        if ('don\'t' in cleaned) and ('know' in cleaned):
            n_idk += 1
        if 'yeah' in cleaned:
            n_yeah += 1
        if 'no' in cleaned:
            n_no += 1
    print('stupid lines: n_idk', n_idk, 'n_yeah', n_yeah, 'n_no', n_no)


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


def batch_tokenizer(lines, need_clean=False):
    cleaner = re.compile('(<u>|</u>|\[|\])')
    vocab_count = {}
    sentences_tokens = []
    for line in lines:
        # TODO: dealing w/ punctuation etc, and do we remove stop words, change he's -> he is etc.
        if need_clean:
            line = cleaner.sub('', line)
        tokens = []
        for token in line.split():
            token = token.lower().strip()
            if token:
                vocab_count[token] = vocab_count.get(token, 0) + 1
                tokens.append(token)
        sentences_tokens.append(tokens)
    return sentences_tokens, vocab_count


def gen_vocab(src, dst, max_words=50000):
    with open(src, 'r') as f:
        sentences_tokens, vocab_count = batch_tokenizer(f)
    print('total words in', src, len(vocab_count))
    # learned from https://github.com/chiphuyen/stanford-tensorflow-tutorials/blob/master/assignments/chatbot/data.py#L127
    vocab_sorted = sorted(vocab_count, key=vocab_count.get, reverse=True)
    vocab = base_vocab_dict()  # pad, unk, s, /s
    offset = len(vocab)
    total = min(max_words, len(vocab_count))
    for i in range(total):
        vocab[vocab_sorted[i]] = offset + i
    with open(dst, 'w') as f:
        json.dump(vocab, f)
    print('wrote', total, 'words to', dst)
