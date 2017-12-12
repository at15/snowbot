import tensorflow as tf
from snowbot.corpus import CORPUS
from snowbot.corpus.util import BatchBucketIterator

DATA_HOME = '../snowbot-data/'


# FIXME: this file only put here because we just want a mega file to do everything to finish #20 fast
def build_encoder():
    print('build encoder')
    word_embeddings = tf.get_variable('word_embeddings', [])


def main():
    print('train!')
    name = 'cornell'
    corpus = CORPUS[name](home=DATA_HOME + name)
    train_val_buckets = corpus.get_buckets()
    train_iter = BatchBucketIterator(
        train_val_buckets['src_train_buckets'],
        train_val_buckets['tgt_train_buckets']
    )
    val_iter = BatchBucketIterator(
        train_val_buckets['src_val_buckets'],
        train_val_buckets['tgt_val_buckets']
    )
    tf.reset_default_graph()


if __name__ == '__main__':
    main()
