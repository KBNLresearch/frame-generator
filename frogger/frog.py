#!/usr/bin/env python
# -*- coding: utf-8 -*-


import socket
import urllib

from flask import Flask, request

application = Flask(__name__)
application.debug = True

class Frog():
    def __init__(self, port=4096):
        self.BUFSIZE = 4096
        self.port = port

    def tag(self, text, html=False):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.settimeout(120.0)
        self.socket.connect(('ontw', self.port))

        text = text.strip(' \t\n')
        text = text.encode('utf-8') + b'\r\nEOT\r\n'
        self.socket.sendall(text)

        res = ''
        done = False
        while not done:
            data = b''
            while not data or data[-1] != b'\n':
                more = self.socket.recv(self.BUFSIZE)
                if not more:
                    break
                data += more
            for line in data.strip(' \t\r\n').split('\n'):
                if line.strip() == 'READY':
                    done = True
                elif line:
                    res += line + "\n"

        self.socket.close()
        return res

@application.route('/')
def index():
    url = request.args.get('url')
    text = request.args.get('text')

    frog = Frog()
    if url:
        data = urllib.urlopen(url).read().decode('utf-8')
        data = data.replace('<text>', '').replace('</text>','')
        data = data.replace('<title>','').replace('</title>','.')
        data = data.replace('<p>','').replace('</p>','')
        return frog.tag(data)

    if text:
        return frog.tag(text)

    return ('No input recieved, either use ?url= or ?text=')

if __name__ == "__main__":

    a="""
    flavour 27% 26% bell hoell 25 '/2 25'A int harv 8% 8'A bemis comp 26'A comp
    26'A —
    """

    b="""inco lim 11% 11 7/8 bausch 25'/2 25 ibm 120 119% beatrice f 28 3 A 28%
    int"""

    f = Frog()
    print f.tag(a.decode('utf-8'))

