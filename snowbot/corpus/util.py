import os
import json
import math
import re
import requests
import tarfile
import zipfile
import gzip
import shutil
import click

import numpy as np

FOO = 'foo'

PAD = '<pad>'
UNKNOWN = '<unk>'
START = '<s>'
END = '</s>'


def base_vocab_dict():
    return {
        PAD: 0,
        UNKNOWN: 1,
        START: 2,
        END: 3
    }


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


def file2ids(src, vocab_json_file):
    with open(src, 'r') as f, open(vocab_json_file, 'r') as fv:
        return sentences2ids(f, json.load(fv))


def sentences2ids(lines, vocab):
    ids = []
    for line in lines:
        ids.append([vocab.get(w, vocab[UNKNOWN]) for w in line.split()])
    return ids


def bucket_ids(src_ids, tgt_ids):
    lens = [len(ids) for ids in src_ids]
    hist, bin_edges = np.histogram(lens, range=(0, 100), bins=10)
    src_buckets = [[] for _ in bin_edges]
    tgt_buckets = [[] for _ in bin_edges]
    for ids, t_ids in zip(src_ids, tgt_ids):
        length = len(ids)
        for j in range(len(bin_edges) - 1, -1, -1):
            if length >= bin_edges[j]:
                src_buckets[j].append(ids)
                tgt_buckets[j].append(t_ids)
                break
    t = 0
    for b in src_buckets:
        t += len(b)
    # print(t, len(src_ids))
    assert t == len(src_ids)
    return src_buckets, tgt_buckets


def convert_size(size_bytes):
    """
    convert size in bytes to human readable string, i.e. 1024 -> 1KB
    copied from https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
    :param size_bytes:
    :return:
    """
    if size_bytes == 0:
        return '0B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '{} {}'.format(s, size_name[i])


def files_exist(folder, files):
    for f in files:
        if not os.path.exists(os.path.join(folder, f)):
            return False
    return True


def files_missing(folder, files):
    missing = []
    for f in files:
        p = os.path.join(folder, f)
        if not os.path.exists(p):
            missing.append(p)
    return missing


def file_head(file, n_lines=10):
    with open(file, errors='ignore') as f:
        for i in range(n_lines):
            print(i, f.readline())


def maybe_download(url, download_dir, silent=False, progress=True):
    def p(*args):
        if not silent:
            print(*args)

    # download file
    file_name = url.split('/')[-1]
    file_path = os.path.join(download_dir, file_name)
    if os.path.exists(file_path):
        p(url, 'has already been downloaded to', file_path)
    else:
        p('downloading', url, 'to', file_path)
        with open(file_path, 'wb') as f:
            res = requests.get(url, stream=True)
            size = res.headers.get('content-length')
            if size and progress:
                size = int(size)
                with click.progressbar(length=size,
                                       label='Downloading {} {}'.format(file_name, convert_size(size))) as bar:
                    for data in res.iter_content(chunk_size=4096):
                        f.write(data)
                        bar.update(len(data))
            else:
                f.write(res.content)  # TODO: don't know if this would work...

    return file_path


def maybe_extract(file, folder, silent=False):
    def p(*args):
        if not silent:
            print(*args)

    if not folder:
        p('extract destination not specified')
        return False
    # gz is single file, not folder
    if file.endswith('.gz'):
        dst_file = os.path.join(folder, file.split('/')[-1][:-3])
        if os.path.exists(dst_file):
            print('file', dst_file, 'already exist, assume already extracted')
            return True
        if not os.path.exists(folder):
            print('create folder', folder)
            os.makedirs(folder)
        print('extract gz file to', dst_file)
        with gzip.open(file, 'rb') as f_in, open(dst_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        return True
    # already extracted
    if os.path.isdir(folder):
        p('folder', folder, 'already exist, assume already extracted')
        return True
    # extract file TODO: can there be progress bar?
    if not os.path.exists(file):
        p(file, 'does not exist')
        return False
    if file.endswith('.zip'):
        zipfile.ZipFile(file=file, mode='r').extractall(folder)
    elif file.endswith('.gz'):
        dst_file = os.path.join(folder, file.split('/')[-1][:-3])
        print('extract gz file to', dst_file)
        with gzip.open(file, 'rb') as f_in, open(dst_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    elif file.endswith(('.tar.gz', '.tgz')):
        tarfile.open(name=file, mode='r:gz').extractall(folder)
    else:
        p('unknown file extension, only support zip, tar.gz but got', file)
        return False
    p('file extracted to', folder)
    return True


def train_test_split(questions, answers, test_ratio, sample=1, shuffle=True):
    assert 0 < test_ratio < 1
    assert 0 < sample <= 1
    assert len(questions) == len(answers)
    total = int(len(questions) * sample)
    if shuffle:
        ids = np.random.permutation(total)
    else:
        ids = np.arange(total)
    test_ids, train_ids = ids[0:int(test_ratio * total)], ids[int(test_ratio * total):]
    train_enc, test_enc, train_dec, test_dec = [], [], [], []
    for i in train_ids:
        train_enc.append(questions[i])
        train_dec.append(answers[i])
    for i in test_ids:
        test_enc.append(questions[i])
        test_dec.append(answers[i])
    return {
        'train_enc': train_enc,
        'train_dec': train_dec,
        'test_enc': test_enc,
        'test_dec': test_dec
    }
