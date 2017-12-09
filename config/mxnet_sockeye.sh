#!/usr/bin/env bash

D_HOME=/home/at15/workspace/src/github.com/at15/snowbot-data/cornell/
M_HOME=/home/at15/workspace/src/github.com/at15/snowbot-model/mxnet_sockeye

python -m sockeye.train --source ${D_HOME}src-train.txt \
                       --target ${D_HOME}tgt-train.txt \
                       --validation-source ${D_HOME}src-val.txt \
                       --validation-target ${D_HOME}tgt-val.txt \
                       --rnn-num-hidden 256 \
                       --output ${M_HOME}

# python -m sockeye.translate --models /home/at15/workspace/src/github.com/at15/snowbot-model/mxnet_sockeye