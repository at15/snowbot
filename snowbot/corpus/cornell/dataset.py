import os
import shutil
import pandas as pd

from snowbot.corpus.util import maybe_download, maybe_extract, files_exist, files_missing

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

    def gen_qa(self):
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
        q, a = os.path.join(self.home, 'q.txt'), os.path.join(self.home, 'a.txt')
        print('save questions and answers to', q, a)
        with open(q, 'w') as f:
            f.write('\n'.join(questions))
        with open(a, 'w') as f:
            f.write('\n'.join(answers))
        return True


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
