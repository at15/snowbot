import tensorflow as tf
from snowbot.corpus import CORPUS
from snowbot.corpus.util import BatchBucketIterator

DATA_HOME = '../snowbot-data/'


# FIXME: this file only put here because we just want a mega file to do everything to finish #20 fast

class Model:
    def __init__(self, src_vocab, tgt_vocab):
        self.src_vocab = src_vocab
        self.tgt_vocab = tgt_vocab
        self.rnn_hidden = 256
        # encoder
        self.encoder_inputs = None
        self.encoder_sequence_length = None
        self.encoder_embed_inputs = None
        self.encoder_state = None
        # decoder
        self.decoder_inputs = None
        self.decoder_sequence_length = None
        self.decoder_embed_inputs = None

    def build_encoder(self):
        print('build encoder')
        # [max_encoder_time, batch_size] NOTE: it's not [batch_size, max_encoder_time] as we used to do,
        # that is because they say this way is faster https://github.com/tensorflow/nmt/issues/84
        # TODO: let our batch iterator yield time major instead of batch major (need to use transpose of numpy ...)
        self.encoder_inputs = tf.placeholder(tf.int32, [100, None])
        # [batch_size]
        self.encoder_sequence_length = tf.placeholder(tf.int32, [None])
        embedding_encoder = tf.get_variable('embedding_encoder',
                                            [len(self.src_vocab), self.rnn_hidden])  # [vocab_size, embed_dim]
        self.encoder_embed_inputs = tf.nn.embedding_lookup(embedding_encoder, self.encoder_inputs)
        encoder_cell = tf.nn.rnn_cell.BasicLSTMCell(self.rnn_hidden)
        # [num_hidden]
        _, self.encoder_state = tf.nn.dynamic_rnn(cell=encoder_cell, inputs=self.encoder_embed_inputs,
                                                  sequence_length=self.encoder_sequence_length,
                                                  time_major=True)

    def build_decoder(self):
        self.decoder_inputs = tf.placeholder(tf.int32, [100, None])
        self.decoder_sequence_length = tf.placeholder(tf.int32, [None])
        embedding_decoder = tf.get_variable('embedding_decoder', [len(self.tgt_vocab), self.rnn_hidden])
        self.decoder_embed_inputs = tf.nn.embedding_lookup(embedding_decoder, self.decoder_inputs)
        decoder_cell = tf.nn.rnn_cell.BasicLSTMCell(self.rnn_hidden)
        helper = tf.contrib.seq2seq.TrainingHelper(
            self.decoder_embed_inputs, self.decoder_sequence_length, time_major=True)


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
