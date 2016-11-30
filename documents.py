#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import gensim
import os
import re
import sys
import time
import urllib

from segtok import segmenter, tokenizer

FROG_URL = 'http://kbresearch.nl/frog/?text='


class DocumentReader(object):

    def __init__(self, input_dir, doc_length=0, pos_tag=True):

        self.regex_dir = input_dir + os.sep + 'regex'
        self.doc_dir = input_dir + os.sep + 'docs'
        self.stop_dir = input_dir + os.sep + 'stop'

        self.doc_length = doc_length
        self.pos_tag = pos_tag

        self.regex_list = self.get_regex(self.regex_dir)
        self.stop_list = self.get_stop_words(self.stop_dir)
        self.doc_list = self.get_documents(self.doc_dir, doc_length)

        self.dictionary = self.get_dictionary(self.doc_list, self.stop_list)
        self.corpus = self.get_corpus()


    def get_regex(self, path):
        print('Processing regular expressions ...')
        regex_list = []
        for filename in [f for f in os.listdir(path) if f[-4:] in ['.txt',
                '.tsv', '.csv']]:
            with open(path + '/' + filename) as f:
                print('Processing file: ' + filename)
                doc = self.decode(f.read())
                lines = [l for l in doc.splitlines() if l]
                regex = [l.split('\t') for l in lines if
                        len(l.split('\t')) == 2]
                regex = [[r[0].strip(), r[1].strip()] for r in regex if
                        r[0].strip() and r[1].strip()]
                regex_list += regex
        print('Number of regular expressions: ' + str(len(regex_list)))
        return regex_list


    def get_stop_words(self, path):
        print('Processing stop words ...')
        stop_list = []
        for filename in [f for f in os.listdir(path) if f.endswith('.txt')]:
            print('Processing file: ' + filename)
            with open(path + os.sep + filename) as f:
                s = self.decode(f.read())
                stop_list += [sw.lower() for sw in s.split() if sw]
        print('Number of stop words: ' + str(len(stop_list)))
        return stop_list


    def get_documents(self, path, doc_length):
        print('Processing documents ...')
        docs = []
        for filename in [f for f in os.listdir(path) if f.endswith('.txt')]:
            with open(path + '/' + filename) as f:
                print('Processing file: ' + filename)
                doc = self.decode(f.read())

                # Process user provided regular expressions
                for regex in self.regex_list:
                    doc = re.sub(regex[0], regex[1], doc, flags=re.I)

                # Remove unwanted characters and whitespace
                unwanted_chars = ['&', '/', '|', '_', ':', '=', '(',
                            ')', '[', ']']
                for char in unwanted_chars:
                    doc = doc.replace(char, '')
                doc = ' '.join(doc.split())

                # Sentence chunk with Segtok
                sentences = [s for s in segmenter.split_single(doc)]

                # Split large documents into smaller parts
                if doc_length > 0:
                    sub_docs = [sentences[i:i + doc_length] for i in
                            xrange(0, len(sentences), doc_length)]
                else:
                    sub_docs = [sentences]

                # Tokenize with Segtok or Frog
                for sub_doc in sub_docs:
                    tokens = []
                    if self.pos_tag:
                        tokens += self.frogger(sub_doc)
                    else:
                        for sentence in sub_doc:
                            tokens += [t.lower() for t in
                                    tokenizer.word_tokenizer(sentence)]
                    docs.append(tokens)

        print('Number of (sub)documents: ' + str(len(docs)))
        return docs


    def frogger(self, to_frog):
        tokens = []
        while len(to_frog):
            i = 0
            data = None
            batch_size = max(10, len(to_frog))
            batch = ' '.join(to_frog[:batch_size]).encode('utf-8')
            while not data:
                if i > 2 and batch_size > 1:
                    print('Reducing batch_size ...')
                    batch_size -= 1
                    batch = ' '.join(to_frog[:batch_size]).encode('utf-8')
                data = urllib.urlopen(FROG_URL + batch).read().decode('utf-8')
                if not data:
                    print('Frog data not found, retrying ...')
                    time.sleep(5)
                    i += 1
            new_tokens = [line.split('\t') for line in data.split('\n') if
                    len(line)]
            tokens += [t[2].lower() + '/' + t[4].split('(')[0] for t in
                    new_tokens if len(t) == 10]
            to_frog = to_frog[batch_size:]
        return tokens


    def get_dictionary(self, doc_list, stop_list):
        print('Generating dictionary ...')
        dictionary = gensim.corpora.Dictionary(self.iter_docs(doc_list,
                stop_list))
        no_below = 1 if len(self.doc_list) <= 10 else 2
        no_above = 1 if len(self.doc_list) <= 10 else 0.95
        dictionary.filter_extremes(no_below=no_below, no_above=no_above,
                keep_n=100000)
        num_tokens = len(dictionary.items())
        print('Number of unique tokens in dictionary: ' + str(num_tokens))
        return dictionary


    def get_corpus(self):
        print('Generating corpus ...')
        corpus = [self.dictionary.doc2bow(text) for text in
                self.iter_docs(self.doc_list, self.stop_list)]
        return corpus


    def iter_docs(self, doc_list, stop_list):
        unwanted_tags = ['LET', 'LID', 'VZ', 'VG']
        for doc in doc_list:
            if self.pos_tag:
                yield (t for t in doc if t.split('/')[0] not in stop_list and
                        len(t.split('/')[0]) > 2 and t.split('/')[1] not in
                        unwanted_tags)
            else:
                yield (t for t in doc if t not in stop_list and len(t) > 2)


    def decode(self, s):
        encodings = ['utf-8', 'iso-8859-1']
        decoded = ''
        for e in encodings:
            try:
                decoded = s.decode(e)
                break
            except UnicodeDecodeError:
                continue
        return decoded

