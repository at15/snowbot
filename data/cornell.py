#!/usr/bin/env python3

import os
import re

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

import click

NAME = 'cornell'
FULL_NAME = 'Cornell Movie Dialog Corpus'
URL = 'https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html'
DATA_URL = 'http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip'

_SEP = '+++$+++'


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
            if not id2line[conv[i]] or not id2line[conv[i + 1]]:
                n_empty += 1
                continue
            questions.append(id2line[conv[i]])
            answers.append(id2line[conv[i + 1]])
    assert len(questions) == len(answers)
    print('skipped', n_empty, 'conversations w/ empty q/a')
    return questions, answers


def batch_tokenizer(lines):
    cleaner = re.compile('(<u>|</u>|\[|\])')
    vocab_count = {}
    sentences_tokens = []
    for l in lines:
        # TODO: dealing w/ punctuation etc, and do we remove stop words, change he's -> he is etc.
        cleaned = cleaner.sub('', l)
        tokens = []
        for token in cleaned.split():
            token = token.lower().strip()
            if token:
                vocab_count[token] = vocab_count.get(token, 0) + 1
                tokens.append(token)
        sentences_tokens.append(tokens)
    return sentences_tokens, vocab_count


@click.command('split')
def split():
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


@click.command('tokenize')
def tokenize():
    src_prefix = 'processed/cornell/'
    dst_prefix = src_prefix


@click.group()
def cli():
    pass


if __name__ == '__main__':
    cli.add_command(txt_to_csv)
    cli.add_command(split)
    cli()
