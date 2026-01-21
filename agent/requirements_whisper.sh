#!/bin/bash -f
sudo apt update
sudo apt install ffmpeg
python -m pip install -U openai-whisper
# python -m pip install git+https://github.com/openai/whisper.git
# python -m pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git
python -m pip install setuptools-rust

