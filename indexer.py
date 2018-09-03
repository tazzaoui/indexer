#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file contains the implementation of the indexer.
Given a set of documents, the indexer will create a
directory by the name of 'index' containing a file for
every term in the corpus.
"""

import os
import base64
import pickle
import logging
from progress.bar import IncrementalBar
from support.token_extract import extract_tokens


class Indexer:
    def __init__(self, verbose=False, path=None):
        self.logger = logging.getLogger("indexer")
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler("indexer.log")
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)
        self.verbose = verbose
        self.path = path

    def create_index(self):
        assert os.path.isdir(self.path), "Nonexistent document directory"
        os.system("rm -rf index; mkdir -p index")
        document_dir = os.fsencode(self.path)
        index = document_count = 0
        for i in os.listdir(document_dir):
            document_count += 1
        bar = IncrementalBar("Processing...", max=21, suffix="%(percent)d%%")
        for document in os.listdir(document_dir):
            file_name = os.fsdecode(document)
            tokens = extract_tokens(os.path.join(self.path, file_name))
            if self.verbose:
                print("Indexing {}".format(base64.b16decode(document)))
                print(tokens)
            for (freq, tok) in tokens:
                file_name = os.path.join(
                    b"index", base64.b16encode(
                        tok.encode()))
                try:
                    f = open(file_name, "rb")
                    token = pickle.load(f)
                    f.close()
                except IOError:
                    token = []
                token.append((freq, document))
                try:
                    token_file = open(file_name, "wb")
                    pickle.dump(token, token_file)
                    token_file.close()
                except Exception as e:
                    self.logger.info("[create_index]: {}".format(e))
                    index -= 1
            if index % int(document_count / 20) == 0:
                self.logger.info("[create_index]: %d/%d", index, document_count)
                bar.next()
            index += 1

    def __del__(self):
        self.logger.info("Object destroyed")