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

import generator
import json
import os
import shutil
import time

from bottle import post, request, route, run

@post('/')
def index():

    try:
        abs_path = os.path.dirname(os.path.realpath(__file__))
        input_dir = abs_path + os.sep + 'input' + os.sep + str(int(time.time()))
        os.makedirs(input_dir)

        doc_dir = input_dir + os.sep + 'docs'
        os.makedirs(doc_dir)
        doc_files = request.files.getall('doc_files[]')
        for f in doc_files:
            name, ext = os.path.splitext(f.filename)
            if ext == '.txt' or ext == '.json':
                f.save(doc_dir)

        stop_dir = input_dir + os.sep + 'stop'
        os.makedirs(stop_dir)
        stop_files = request.files.getall('stop_files[]')
        for f in stop_files:
            name, ext = os.path.splitext(f.filename)
            if ext == '.txt':
                f.save(stop_dir)

        regex_dir = input_dir + os.sep + 'regex'
        os.makedirs(regex_dir)
        regex_files = request.files.getall('regex_files[]')
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

        _, keyword_list, frame_list = generator.generate(dlen=10, kcount=5,
                ktags=keyword_tags, wdir=window_direction, wsize=window_size,
                ftags=frame_tags, input_dir=input_dir, output_dir=None, fsize=8)

        max_kscore = max([k[1] for k in keyword_list.keywords])
        max_fscores = []
        for frame in frame_list.frames:
            if frame:
                max_fscores.append(max([f[1] for f in frame]))
        max_fscore = max(max_fscores)

        data = {'frames': []}
        for i, k in enumerate(keyword_list.keywords):
            d = {}
            d['keyword'] = {k[0].encode('utf-8'): k[1] / max_kscore}
            d['frame'] = {}
            for f in frame_list.frames[i]:
                d['frame'][f[0].encode('utf-8')] = f[1] / max_fscore
            data['frames'].append(d)

        result = json.dumps(data)

    except Exception as e:
        result = json.dumps({'error': repr(e)})

    finally:
        if 'input_dir' in locals():
            if os.path.isdir(input_dir):
                shutil.rmtree(input_dir)

    print result
    return result


if __name__ == '__main__':
    run(host='localhost', port=8091)

