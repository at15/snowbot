#!/usr/bin/env python3

import os
import click

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

NAME = 'cornell'
FULL_NAME = 'Cornell Movie Dialog Corpus'
URL = 'https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html'
DATA_URL = 'http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip'

_SEP = '+++$+++'

def to_csv(src, dst, columns, array_col=-1, escape_col=-1):
    """Convert the original Cornell Movie Dialog corpus to csv because pandas can't load it directly

    The original text is separated by +++$+++, when using pandas, it is treated as regular expression,
    and pandas will switch to python engine and fail. Also it contains comma because certain fields like
    genres and lines are array ['L102', 'L103'].

    After conversion, it becomes a csv, and array is converted to 'L102','L103'. Space are trimmed,
    quote is added for escape_col, only movie_lines.txt has string that need to be quoted

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


def get_id2line(csv_file):
    df = pd.read_csv(csv_file)
    df = df.fillna('')
    id2line = {}
    for line_id, line in zip(df['id'], df['utterance']):
        id2line[line_id] = line
    return id2line


def get_conversations(csv_file):
    df = pd.read_csv(csv_file)
    convs = []
    for conv in df['lines']:
        # str 'L1'; 'L2' -> list [L1, L2]
        convs.append([l.strip()[1:-1] for l in conv.split(';')])
    return convs


def get_qa(prefix='processed/cornell/'):
    convs = get_conversations(prefix + 'movie_conversations.csv')
    id2line = get_id2line(prefix + 'movie_lines.csv')
    questions, answers = [], []
    n_empty = 0
    for conv in convs:
        for i in range(len(conv) - 1):
            if not id2line[conv[i]] or not id2line[conv[i+1]]:
                n_empty += 1
                continue
            questions.append(id2line[conv[i]])
            answers.append(id2line[conv[i + 1]])
    assert len(questions) == len(answers)
    print('skipped', n_empty, 'conversations w/ empty q/a')
    return questions, answers


@click.command('convert')
def convert():
    dst_prefix = 'processed/cornell/'
    questions, answers = get_qa()
    for i in range(6):
        print('Q:', questions[i])
        print('A:', answers[i], '\n')
    # TODO: it could be better to split test and train based on conversation id instead of qa id
    test_ratio = 0.1
    total = len(questions)
    ids = np.random.permutation(total)
    test_ids, train_ids = ids[0:int(test_ratio * total)], ids[int(test_ratio * total):]
    print('test ids', len(test_ids))
    train_enc, test_enc, train_dec, test_dec = [], [], [], []
    for i in train_ids:
        train_enc.append(questions[i])
        train_dec.append(answers[i])
    for i in test_ids:
        test_enc.append(questions[i])
        test_dec.append(answers[i])
    print(len(train_enc), len(train_dec), len(test_enc), len(test_dec))
    for name, data in zip(['train_enc.txt', 'train_dec.txt', 'test_enc.txt', 'test_dec.txt'],
                          [train_enc, train_dec, test_enc, test_dec]):
        print('write to', name)
        with open(dst_prefix + name, 'w') as f:
            f.write('\n'.join(data))
    print('done')


@click.command('csv')
def txt_to_csv():
    raw_prefix = 'raw/cornell/'
    csv_prefix = 'processed/cornell/'
    if not os.path.exists(raw_prefix):
        print('raw folder not found', raw_prefix)
    if not os.path.exists(csv_prefix):
        os.makedirs(csv_prefix)
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
        to_csv(raw_prefix + f + '.txt', csv_prefix + f + '.csv', m['cols'], array_col, escape_col)


@click.group()
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(txt_to_csv)
    cli.add_command(convert)
    cli()
