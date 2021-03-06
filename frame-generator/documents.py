#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Frame Generator
#
# Copyright (C) 2016 Juliette Lonij, Koninklijke Bibliotheek -
# National Library of the Netherlands
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import gensim
import io
import json
import os
import re
import sys
import time
import urllib

from lxml import etree
from segtok import segmenter
from segtok import tokenizer

FROG_URL = 'http://www.kbresearch.nl/frogger/?'


class DocumentReader(object):
    '''
    Process input documents.
    '''

    def __init__(self, input_dir, doc_length=0, pos_tag=True):
        '''
        Create regex list, stop word list, document list, dictionary and corpus.
        '''
        self.regex_dir = input_dir + os.sep + 'regex'
        self.doc_dir = input_dir + os.sep + 'docs'
        self.stop_dir = input_dir + os.sep + 'stop'

        self.doc_length = doc_length
        self.pos_tag = pos_tag

        self.log = []

        self.regex_list = self.get_regex(self.regex_dir)
        self.stop_list = self.get_stop_words(self.stop_dir)
        self.doc_list = self.get_documents(self.doc_dir, doc_length)

        self.dictionary = self.get_dictionary(self.doc_list, self.stop_list)
        self.corpus = self.get_corpus()

    def get_regex(self, path):
        '''
        Create regex list from input documents.
        '''
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
        '''
        Create stop word list from input documents.
        '''
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
        '''
        Create document list from input documents.
        '''
        print('Processing documents ...')
        docs = []
        for filename in [f for f in os.listdir(path) if f[-4:] in ['.txt',
                '.xml']]:
            with open(path + '/' + filename) as f:
                print('Processing file: ' + filename)

                # Remove xml tags and decode
                if filename.endswith('.xml'):
                    xml = etree.fromstring(f.read())
                    text = etree.tostring(xml, encoding='utf-8', method='text')
                    doc = text.decode('utf-8')
                else:
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
                        tokens += self.frogger(sub_doc, filename)
                    else:
                        for sentence in sub_doc:
                            tokens += [t.lower() for t in
                                    tokenizer.word_tokenizer(sentence)]
                    if len(tokens):
                        docs.append(tokens)

        for filename in [f for f in os.listdir(path) if f.endswith('.json')]:
            with open(path + '/' + filename) as f:
                print('Processing file: ' + filename)
                docs += json.load(f)['docs']

        print('Number of (sub)documents: ' + str(len(docs)))
        assert docs, 'No documents found'

        return docs

    def frogger(self, to_frog, filename):
        '''
        Process document with Frog web service.
        '''
        tokens = []
        while len(to_frog):
            batch_size = min(10, len(to_frog))
            batch = ' '.join(to_frog[:batch_size])
            query_string = urllib.urlencode({'text': batch.encode('utf-8')})

            i = 0
            data = None
            while not data:
                try:
                    data = urllib.urlopen(FROG_URL + query_string)
                    data = data.read().decode('utf-8')
                except IOError:
                    if i < 2:
                        print('Frog data not found, retrying ...')
                        time.sleep(10)
                        i += 1
                    else:
                        print('Frog data not found, skipping document!')
                        self.log.append('Frog data not found for (part of): ' +
                                filename)
                        return []

            new_tokens = [line.split('\t') for line in data.split('\n')
                    if len(line)]
            try:
                assert len(new_tokens[0]) == 10, 'Frog data invalid'
                tokens += [t[2].lower() + '/' + t[4].split('(')[0] for t in
                        new_tokens if len(t) == 10]
            except AssertionError:
                print('Frog data invalid, skipping document!')
                self.log.append('Frog data invalid for (part of): ' + filename)
                return []

            to_frog = to_frog[batch_size:]

        return tokens

    def get_dictionary(self, doc_list, stop_list):
        '''
        Create dictionary from document and stop word lists.
        '''
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
        '''
        Create corpus.
        '''
        print('Generating corpus ...')
        corpus = [self.dictionary.doc2bow(text) for text in
                self.iter_docs(self.doc_list, self.stop_list)]
        return corpus

    def iter_docs(self, doc_list, stop_list):
        '''
        Generate tokens from document and stop word lists.
        '''
        unwanted_tags = ['LET', 'LID', 'VZ', 'VG']
        for doc in doc_list:
            if self.pos_tag:
                yield (t for t in doc if t.split('/')[0] not in stop_list and
                        len(t.split('/')[0]) > 2 and t.split('/')[1] not in
                        unwanted_tags)
            else:
                yield (t for t in doc if t not in stop_list and len(t) > 2)

    def decode(self, s):
        '''
        Decode utf-8 and iso-8859-1 encoded strings.
        '''
        encodings = ['utf-8', 'iso-8859-1']
        decoded = ''
        for e in encodings:
            try:
                decoded = s.decode(e)
                break
            except UnicodeDecodeError:
                continue
        return decoded

    def save_docs(self, output_dir):
        '''
        Save processed documents to file.
        '''
        data = {'docs': self.doc_list}
        with io.open(output_dir + os.sep + 'docs.json', 'w',
                encoding='utf-8') as f:
            f.write(unicode(json.dumps(data, ensure_ascii=False)))
        if self.log:
            with open(output_dir + os.sep + 'log' + '.txt', 'w') as f:
                for line in self.log:
                    f.write(line + '\n')
