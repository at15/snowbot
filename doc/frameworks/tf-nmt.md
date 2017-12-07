# Tensorflow nmt

https://github.com/tensorflow/nmt

## Usage

### Data

- data size is around 4G ... token a long time to process, seems to be written in pure python, or because I am running OpenNMT-tf

````sh
nmt/scripts/wmt16_en_de.sh /tmp/wmt16
````

train

````
python -m nmt.nmt \
    --src=de --tgt=en \
    --hparams_path=nmt/standard_hparams/wmt16_gnmt_4_layer.json \
    --out_dir=/tmp/deen_gnmt \
    --vocab_prefix=/tmp/wmt16/vocab.bpe.32000 \
    --train_prefix=/tmp/wmt16/train.tok.clean.bpe.32000 \
    --dev_prefix=/tmp/wmt16/newstest2013.tok.bpe.32000 \
    --test_prefix=/tmp/wmt16/newstest2015.tok.bpe.32000
````

`head vocab.bpe.32000` it mixed english and german, along with the `@@` stuff, seems to be for BPE, train data is 790 M ... I won't try that for sure ....

````
<unk>
<s>
</s>
,
.
the
in
of
and
die
````