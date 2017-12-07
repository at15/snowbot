# Sockeye

https://github.com/awslabs/sockeye

## Usage

````sh
# NOTE: by default mxnet-1.0 will be installed, but sockeye requires 0.12, so 1.0 will be uninstalled, unless using virtualenv
# pip install mxnet-cu80
wget https://raw.githubusercontent.com/awslabs/sockeye/master/requirements.gpu-cu80.txt
pip install sockeye --no-deps -r requirements.gpu-cu80.txt
rm requirements.gpu-cu80.txt
````

## Tutorials

- https://blog.kovalevskyi.com/step-by-step-guide-for-creating-a-chatbot-with-sockeye-mxnet-aws-ec2-and-deeplearning-ami-259f443abf3e