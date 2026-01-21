#!/bin/bash -f
export SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True
pip3 install -r ../config/3pp/_requirements.txt
# python3 -m spacy download en
spacy download en
# python3 -m spacy download en_core_web_sm

