import sys
import tensorflow as tf

# source env/bin/activate
print(sys.version)

# pip install --ignore-installed --upgrade https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow_gpu-1.3.0-cp36-cp36m-linux_x86_64.whl
print('tensorflow version', tf.__version__)
