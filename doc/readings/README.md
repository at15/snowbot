# Readings

## Papers

2014

[Sequence to Sequence Learning with Neural Networks](https://arxiv.org/pdf/1409.3215.pdf)

- simplest strategy for general sequence learning is to map the input sequence to a fixed size using one RNN, 
and then to map the vector to the target sequence with another RNN
  - [ ] this fixed size vector is the hidden state? or the aggregated output from each step?
- two different LSTM, one for input, one for ouput
- 4 layer LSTM
- use simple left-to-right beam search decoder
 - [ ] TODO: performs well even with a beam size of 1?
- **extremely valuable to reverse the order of the words of the input sentence**
  - LSTM learns much better when the source sentences are reversed (the target sentences are not reversed)
  
## Reports

Stanford cs224n 

- [A Neural Chatbot with Personality](https://web.stanford.edu/class/cs224n/reports/2761115.pdf)
  - reverse encoder to retain more from the beginning of the utterance
  - greedy, use the most likely token at each decoder step
  - doesn't use start token or end token for encoders, use only end token for decoders, character token is used to signal beginning of a response
  - use sampled softmax because vocabulary is too large in cornell dataset
  - use buckets `[(15, 15), (25, 25) ...]` encoder length, decoder length ...
  - [ ] feed previously predicted tokens to predict the next token to make the train env similar to test
  - pre trained (GLoVe) sucks ... (as usual for small dataset)
  - visualized embedding
  
## Lectures

Stanford cs224n Lecture 10 [NMT and Attention](https://web.stanford.edu/class/cs224n/lectures/cs224n-2017-lecture10.pdf)

- P51 Decoders, brutal force, exhaustive search (won't work)
- P52-53 Ancestral Sampling, high variance
- P54 Greedy, most likely symbol each time
  - [ ] how to know which one is most likely? 

## Code

[tensorflow/nmt](https://github.com/tensorflow/nmt/tree/tf-1.4)

- [ ] NOTE: tf-1.4 seq2seq has bug ...
- encoder: consume the input source words without making any prediction
- decoder: processing the target sentence while predicting the next words
- train
  - input: source sentence `<s>` target sentence (`你吃了么 <s> Have you eat`) 酱?
  - encoder_inputs [mx_encoder_time, batch_size] source input words `你吃了么`
  - decoder_inputs [max_decoder_time, batch_size] target input words `<s> Have you eat`
  - decoder_outputs [max_decoder_time, batch_size] target output words, 
decoder_inputs shifted to left by one time step with an end-of-sentence tag appended on the right. `Have you eat </s>`
- embedding
  - vocabulary is required, most frequent V words are kept, other treated as unknown
- encoder
  - pass `sequence_length` with `target_sequence_length`
  - [x] SOLVED: time_major=True? https://github.com/tensorflow/nmt/issues/84, it is faster (I was using batch major in previous assignments)
- decoder
  - initialize it with last hidden state of the encoder `encoder_state`
  - `decoder_lengths` means `target_sequence_length` I guess?
  - [ ] TrainingHelper can be substituted with GreedyEmbeddingHelper to do greedy decoding
  - `output_layer` is `projection_layer`, turn top hidden states to logit vectors of dimension V (vocab size) for calc loss
    - `projection_layer = tf.layers.Dense(tgt_vocab_size, use_bias=False)`
    - [x] SOLVED: in [API dpc](https://www.tensorflow.org/api_docs/python/tf/layers/dense), it needs `inputs` and `units`, but it seems only `units` is passed in
      - it created class `Dense` while in doc, `dense` the function requires input to apply to
    - [ ] dense is the fully connected layer right? W * X + B
- loss
  - `sparse_softmax_cross_entropy_with_logits`
  - [ ] `labels` is not `decoder_outputs` but `target_outputs` in real code
  - when calculate loss, `target_weights` is used to masks padding positions outside of the target sequence length w/ values 0
    - `tf.sequence_mask(target_sequence_length, max_time, dtype=logits.dtype)`
  - [ ] NOTE: invariant to batch_size, have difference in hyper parameter tuning
- gradient computation & optimization
  - clip gradients `tf.clip_by_global_norm`, (not just one line call to AdamOptimizer)
  -