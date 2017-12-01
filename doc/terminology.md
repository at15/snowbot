# Terminology

- context: the conversation so far [1][1]
- utterance: response [1][1]
- recall@k: pick k best among 10 possible (1 true and 9 distractors). If the correct one is among the picked one, we mark the example as correct
  - 9 distractors were picked at random, in realword Goolge use cluster to compe up with possible response [Smart Reply][2]

[1]: http://www.wildml.com/2016/07/deep-learning-for-chatbots-2-retrieval-based-model-tensorflow/
[2]: https://arxiv.org/abs/1606.04870