# Seq2Seq on Tensorflow

- tf has [new seq2seq](https://www.tensorflow.org/api_guides/python/contrib.seq2seq), some examples are using [legacy seq2seq](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/contrib/legacy_seq2seq/python/ops/seq2seq.py)
  - [tf.contrib.seq2seq](https://www.tensorflow.org/api_docs/python/tf/contrib/seq2seq)
  - [tf.contrib.legacy_seq2seq](https://www.tensorflow.org/api_docs/python/tf/contrib/legacy_seq2seq)
- official wrappers
  - [google/seq2seq](https://github.com/google/seq2seq)
    - it also mentioned http://opennmt.net/
  - [google/tensor2tensor](https://github.com/tensorflow/tensor2tensor)
  - [tensorflow/nmt](https://github.com/tensorflow/nmt/tree/tf-1.4)
    - provides detail instruction, using the new API
  
Popular code using legacy seq2seq `tf.contrib.legacy_seq2seq`

- https://github.com/suriyadeepan/practical_seq2seq/blob/master/seq2seq_wrapper.py
- https://github.com/chiphuyen/stanford-tensorflow-tutorials/tree/master/assignments/chatbot
  - it is using `tf.nn.seq2seq`, which is even older than `tf.contrib.legacy_seq2seq`