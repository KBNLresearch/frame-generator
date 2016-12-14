#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import unicodecsv as csv
import documents
import frames
import keywords
import models
import os
import sys
import time


def save_settings(args, output_dir):

    if args['gtype'] == 'topics':
        output_args = ['gtype', 'dlen', 'tcount', 'tsize', 'mallet']
    elif args['gtype'] == 'keywords' or args['gtype'] == 'frames':
        output_args = ['gtype', 'dlen', 'kmodel', 'kcount', 'ktags']
        if args['kmodel'] == 'lda':
            output_args += ['tcount', 'tsize', 'mallet']
        if args['gtype'] == 'frames':
            output_args += ['wdir', 'wsize', 'fsize', 'ftags']

    with open(output_dir + os.sep + 'settings' + '.csv', 'wb') as f:
        csv_writer = csv.writer(f, delimiter='\t', encoding='utf-8')
        for arg in output_args:
            csv_writer.writerow([arg, str(args[arg])])


def generate(gtype='frames', dlen=0, pos=True, tcount=10, tsize=10, mallet=None,
            kmodel='lda', kcount=10, ktags=[], wdir=None, wsize=5, fsize=10,
            ftags=[], input_dir='input', output_dir='output'):

    # Create input, output directory
    if output_dir == 'output':
        output_dir += os.sep + str(int(time.time()))
        os.makedirs(output_dir)

    # Save settings
    if output_dir:
        save_settings(locals(), output_dir)

    # Generate document list, dictionary and corpus
    doc_reader = documents.DocumentReader(input_dir, dlen, pos)
    if output_dir:
        doc_reader.save_docs(output_dir)

    # Generate only topics
    if gtype == 'topics':
        topic_list = models.TopicList(doc_reader, tcount, tsize, mallet)
        if output_dir:
            topic_list.save_topics(output_dir)
        return topic_list, None, None

    # Generate keywords based on tf-idf scores
    if kmodel == 'tf-idf':
        tfidf_list = models.TfIdfList(doc_reader)
        keyword_list = keywords.KeywordList(doc_reader, kcount, ktags,
                tfidf_list=tfidf_list)
        if output_dir:
            keyword_list.save_keywords(output_dir)

    # Generate keywords based on topics
    else:
        topic_list = models.TopicList(doc_reader, tcount, tsize, mallet)
        if output_dir:
            topic_list.save_topics(output_dir)
        keyword_list = keywords.KeywordList(doc_reader, kcount, ktags,
                topic_list=topic_list)
        if output_dir:
            keyword_list.save_keywords(output_dir)

    # Generate only keywords
    if gtype == 'keywords':
        return None, keyword_list, None

    # Generate frames based on generated keywords
    else:
        frame_list = frames.FrameList(doc_reader, keyword_list, wdir, wsize,
                fsize, ftags)
        if output_dir:
            frame_list.save_frames(output_dir)
        return None, keyword_list, frame_list


if __name__ == '__main__':
    if sys.stdout.encoding != 'UTF-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout, 'strict')

    parser = argparse.ArgumentParser()

    # Generator arguments
    parser.add_argument('--gtype', required=False, type=str, default='frames',
            help='type of generator: topics, keywords or frames')

    # Corpus arguments
    parser.add_argument('--dlen', required=False, type=int, default=0,
            help='number of sentences per document')
    parser.add_argument('--nopos', required=False, action='store_false',
            help='do not apply pos-tagging')

    # Topics arguments
    parser.add_argument('--tcount', required=False, type=int, default=10,
            help='number of topics')
    parser.add_argument('--tsize', required=False, type=int, default=10,
            help='number of words per topic')
    parser.add_argument('--mallet', required=False, type=str,
            help='path to Mallet executable')

    # Keywords arguments
    parser.add_argument('--kmodel', required=False, type=str, default='lda',
            help='keyword scoring model: tf-idf or lda')
    parser.add_argument('--kcount', required=False, type=int, default=10,
            help='number of keywords')
    parser.add_argument('--ktags', required=False, type=str, nargs='*',
            default=[], help='keyword pos-tags')

    # Frames arguments
    parser.add_argument('--wdir', required=False, type=str,
            help='window direction: left or right')
    parser.add_argument('-wsize', required=False, type=int, default=5,
            help='window size')
    parser.add_argument('--fsize', required=False, type=int, default=10,
            help='number of words per frame')
    parser.add_argument('--ftags', required=False, type=str, nargs='*',
            default=[], help='frame pos-tags')

    args = parser.parse_args()

    topic_list, keyword_list, frame_list = generate(gtype=vars(args)['gtype'],
            dlen=vars(args)['dlen'], pos=vars(args)['nopos'],
            tcount=vars(args)['tcount'], tsize=vars(args)['tsize'],
            mallet=vars(args)['mallet'], kmodel=vars(args)['kmodel'],
            kcount=vars(args)['kcount'], ktags=vars(args)['ktags'],
            fsize=vars(args)['fsize'], ftags=vars(args)['ftags'],
            wdir=vars(args)['wdir'], wsize=vars(args)['wsize'])

    if frame_list:
        frame_list.print_frames()
    elif keyword_list:
        keyword_list.print_keywords()
    elif topic_list:
        topic_list.print_topics()

