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