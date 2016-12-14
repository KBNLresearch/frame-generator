#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unicodecsv as csv
import gensim
import os

class TopicList(object):

    def __init__(self, doc_reader, num_topics=10, num_words=10,
            mallet_path=None):

        self.doc_reader = doc_reader
        self.num_topics = num_topics
        self.num_words = num_words
        self.mallet_path = mallet_path

        if mallet_path:
            print('Generating Mallet LDA model ...')
            lda = gensim.models.wrappers.LdaMallet(mallet_path,
                    num_topics=num_topics, corpus=self.doc_reader.corpus,
                    id2word=self.doc_reader.dictionary)
            self.topics = lda.show_topics(num_topics=num_topics,
                    num_words=num_words, formatted=False)
        else:
            print('Generating Gensim LDA model ...')
            lda = gensim.models.LdaModel(corpus=self.doc_reader.corpus,
                    id2word=self.doc_reader.dictionary, num_topics=num_topics,
                    alpha='auto', chunksize=1, eval_every=1)
            gensim_topics = [t[1] for t in lda.show_topics(num_words=num_words,
                    num_topics=num_topics, formatted=False)]
            self.topics = [[(i[1], i[0]) for i in t] for t in gensim_topics]


    def save_topics(self, dir_name):
        with open(dir_name + os.sep + 'topics' + '.csv', 'wb') as f:
            csv_writer = csv.writer(f, delimiter='\t', encoding='utf-8')
            for topic in self.topics:
                csv_writer.writerow([t[1] for t in topic])
                csv_writer.writerow([str(t[0]) for t in topic])


    def print_topics(self):
        print('Topics generated:')
        for i, topic in enumerate(self.topics):
            print('[' + str(i + 1) + '] ' + ', '.join([t[1] for t in topic]))


class TfIdfList(object):

    def __init__(self, doc_reader):

        self.doc_reader = doc_reader

        print('Generating Gensim TF-IDF model ...')
        tfidf = gensim.models.TfidfModel(self.doc_reader.corpus)
        self.scores = tfidf[self.doc_reader.corpus]

