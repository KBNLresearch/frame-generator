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
import math
import operator
import os
import unicodecsv as csv


class KeywordList(object):
    '''
    List of generated keywords.
    '''

    def __init__(self, doc_reader, num_keywords=10, keyword_tags=[],
            topic_list=None, tfidf_list=None):
        '''
        Set KeywordList attributes.
        '''
        self.doc_reader = doc_reader
        self.num_keywords = num_keywords
        self.keyword_tags = keyword_tags
        self.topic_list = topic_list
        self.tfidf_list = tfidf_list

        self.keywords = self.generate_keywords()

    def generate_keywords(self):
        '''
        Generate keywords.
        '''
        print('Generating keywords ...')
        keywords = {}

        if self.tfidf_list:
            for doc in self.tfidf_list.scores:
                for t in doc:
                    key = self.doc_reader.dictionary.get(t[0])
                    score = t[1]
                    if key in keywords:
                        keywords[key] += score
                    else:
                        keywords[key] = score

        elif self.topic_list:
            # Sum of probabilities for token in all topics
            for topic in self.topic_list.topics:
                for t in topic:
                    if t[1] in keywords:
                        keywords[t[1]] += t[0]
                    else:
                        keywords[t[1]] = t[0]

            # Probability for each token multiplied by token frequency
            matrix = gensim.matutils.corpus2csc(self.doc_reader.corpus)
            for token, pr in keywords.items():
                for dict_tuple in self.doc_reader.dictionary.items():
                    if dict_tuple[1] == token:
                        token_index = dict_tuple[0]
                        break
                token_row = matrix.getrow(token_index)
                token_freq = token_row.sum(1).item()
                keywords[token] = pr * math.log(token_freq)

        # Sort keywords by highest score
        sorted_keywords = sorted(keywords.items(), key=operator.itemgetter(1),
                reverse=True)

        # Filter wanted keyword tags
        if self.keyword_tags:
            sorted_keywords = [k for k in sorted_keywords if k[0].split('/')[1]
                    in self.keyword_tags]

        return sorted_keywords[:self.num_keywords]

    def print_keywords(self):
        '''
        Print generated keywords.
        '''
        print('Keywords generated:')
        for i, k in enumerate(self.keywords):
            print('(' + str(i + 1) + ') ' + k[0] + ' [' + str(k[1]) + ']')

    def save_keywords(self, dir_name):
        '''
        Save generated keywords to file.
        '''
        with open(dir_name + os.sep + 'keywords' + '.csv', 'wb') as f:
            # Manually encode a BOM, utf-8-sig didn't work with unicodecsv
            f.write(u'\ufeff'.encode('utf8'))
            csv_writer = csv.writer(f, delimiter='\t', encoding='utf-8')
            for k in self.keywords:
                csv_writer.writerow([k[0], str(k[1])])
