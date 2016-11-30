#!/usr/bin/env python
# -*- coding: utf-8 -*-

import generator
import os
import time

from bottle import get, post, request, route, run, template

@get('/')
def index():
    return template('web' + os.sep + 'index')

@post('/')
def result():
    input_dir = 'input' + os.sep + str(int(time.time()))
    os.makedirs(input_dir)
    output_dir = 'output' + os.sep + str(int(time.time()))
    os.makedirs(output_dir)

    doc_dir = input_dir + os.sep + 'docs'
    os.makedirs(doc_dir)
    doc_files = request.files.getall('doc_files')
    for f in doc_files:
        name, ext = os.path.splitext(f.filename)
        if ext == '.txt':
            f.save(doc_dir)

    stop_dir = input_dir + os.sep + 'stop'
    os.makedirs(stop_dir)
    stop_files = request.files.getall('stop_files')
    for f in stop_files:
        name, ext = os.path.splitext(f.filename)
        if ext == '.txt':
            f.save(stop_dir)

    regex_dir = input_dir + os.sep + 'regex'
    os.makedirs(regex_dir)
    regex_files = request.files.getall('regex_files')
    for f in regex_files:
        name, ext = os.path.splitext(f.filename)
        if ext == '.txt':
            f.save(regex_dir)

    window_size = int(request.forms.get('window_size'))
    window_direction = request.forms.get('window_direction')

    frame_tags = []
    for i in range(1, 13):
        if request.forms.get('ftag' + str(i)):
            frame_tags.append(request.forms.get('ftag' + str(i)))

    keyword_tags = []
    for i in range(1, 13):
        if request.forms.get('ktag' + str(i)):
            keyword_tags.append(request.forms.get('ktag' + str(i)))

    _, keyword_list, frame_list = generator.generate(dlen=10, ktags=keyword_tags,
            wdir=window_direction, wsize=window_size, ftags=frame_tags,
            input_dir=input_dir, output_dir=output_dir)

    return template('web' + os.sep + 'results',
            keywords=keyword_list.keywords, frames=frame_list.frames)


if __name__ == '__main__':
    run(host='localhost', port=8080)

