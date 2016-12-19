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

import unicodecsv as csv
import math
import operator
import os

class FrameList(object):

    def __init__(self, doc_reader, keyword_list, window_direction=None,
        window_size=5, frame_size=10, frame_tags=[]):

        self.doc_reader = doc_reader
        self.keyword_list = keyword_list
        self.window_direction = window_direction
        self.window_size = window_size
        self.frame_size = frame_size
        self.frame_tags = frame_tags

        self.frames = self.generate_frames(self.keyword_list.keywords,
                self.doc_reader.doc_list)


    def generate_frames(self, keywords, docs):
        print('Generating frames ...')

        frames = []
        for k in keywords:
            frame = {}
            for doc in docs:
                for i, t in enumerate(doc):

                    # Find all occurences of the keyword in the doc bow
                    if t == k[0]:
                        # Get the window indeces
                        if self.window_direction == 'left':
                            window_indices = range(i - self.window_size, i)
                        elif self.window_direction == 'right':
                            window_indices = range(i + 1,
                                    i + self.window_size + 1)
                        else:
                            window_indices = (range(i - self.window_size, i) +
                                    range(i + 1, i + self.window_size + 1))

                        # Find the words in the keyword window
                        for w in [word for word in doc if doc.index(word)
                                in window_indices]:

                            # Check if word meets frame criteria
                            if (len(w.split('/')[0]) > 2 and w.split('/')[0] not
                                    in self.doc_reader.stop_list):
                                if (not self.frame_tags or w.split('/')[1] in
                                        self.frame_tags):

                                    # Calculate score for selected word
                                    distance = abs(i - doc.index(w))
                                    score = math.exp(distance * -0.25)

                                    # Add word and score to frame dict
                                    if w in frame:
                                        frame[w] += score
                                    else:
                                        frame[w] = score

            # Sort frame by highest score
            sorted_frame = sorted(frame.items(), key=operator.itemgetter(1),
                    reverse=True)[:self.frame_size]

            frames.append(sorted_frame)

        return frames


    def print_frames(self):
        print('Keywords and frames generated:')
        for i, k in enumerate(self.keyword_list.keywords):
            print('(' + str(i + 1) + ') ' + k[0] + ' [' + str(k[1]) + ']')
            print(', '.join([f[0] + ' (' + str(f[1]) + ')' for f in
                    self.frames[i]]))


    def save_frames(self, dir_name):
        with open(dir_name + os.sep + 'frames' + '.csv', 'wb') as f:
            # Manually encode a BOM, utf-8-sig didn't work with unicodecsv
            f.write(u'\ufeff'.encode('utf8'))
            csv_writer = csv.writer(f, delimiter='\t', encoding='utf-8')
            for i, frame in enumerate(self.frames):
                csv_writer.writerow([self.keyword_list.keywords[i][0]] +
                        [f[0] for f in frame])
                csv_writer.writerow([self.keyword_list.keywords[i][1]] +
                        [str(f[1]) for f in frame])
