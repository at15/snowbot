# OpenNMT-tf

https://github.com/OpenNMT/OpenNMT-tf

## Usage

- [ ] TODO: how long the toy data takes
  - default is 1000000 steps, seems to be 3s per step (based on tensorboard it's 0.3 per step)
  - takes 83h .... so I just stop it .... the infer is working, use latest checkpoint

````sh
# build vocab for toy data
python -m bin.build_vocab --size 50000 --save_vocab data/toy-ende/src-vocab.txt data/toy-ende/src-train.txt
python -m bin.build_vocab --size 50000 --save_vocab data/toy-ende/tgt-vocab.txt data/toy-ende/tgt-train.txt
# train
python -m bin.main train --model config/models/nmt_small.py --config config/opennmt-defaults.yml config/data/toy-ende.yml
# test
python -m bin.main infer --config config/opennmt-defaults.yml config/data/toy-ende.yml --features_file data/toy-ende/src-test.txt
````