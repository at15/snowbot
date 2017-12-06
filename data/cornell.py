#!/usr/bin/env python3

import os
import click

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


@click.command('csv')
def all_to_csv():
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
    cli.add_command(all_to_csv)
    cli()
