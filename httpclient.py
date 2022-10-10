#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return "Code: " + str(self.code) + '\nBody: \n' + self.body

class HTTPClient(object):
    #def get_host_port(self,url):

    def __init__(self):
        self.port = 80

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        #assumes that code is the 2nd thing in the first line of data, which is separated by '\r\n'
        #return int(data.split('\r\n')[0].split(' ')[1])
        splits = data.split('\r\n')
        if len(splits) > 0:
            newSplits = splits[0].split(' ')
            if len(newSplits) > 1:
                return int(newSplits[1])
        return 400

    def get_headers(self,data):
        #assumes that headers are are the 2nd line of data -> line before body
        return '\r\n'.join(data.split('\r\n\r\n')[0].split('\r\n')[1:])

    def get_body(self, data):
        #return data.split('\r\n\r\n')[1]
        splits = data.split('\r\n\r\n')
        if len(splits) > 1:
            return splits[1]
        return ''
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def parse_url(self, url):
        info = {"path" : None, "port": None, "hostname" : None}
        parsed = urllib.parse.urlparse(url)#has path, port, and hostname
        if not parsed.path:
            info["path"] = "/"
        else:
            info["path"] = parsed.path

        if not parsed.port:
            info["port"] = 80
        else:
            info["port"] = parsed.port

        if not parsed.hostname:
            info["hostname"] = parsed.path
            info["path"] = "/"
        else:
            info["hostname"] = parsed.hostname

        return info          

    def GET(self, url, args=None):
        info = self.parse_url(url)
        self.connect(info["hostname"], info["port"])

        request = f'GET {info["path"]} HTTP/1.0\r\nHost: {info["hostname"]}:{info["port"]}\r\nConnection: Close\r\n\r\n'

        self.sendall(request)

        receivedMessage = self.recvall(self.socket)
        self.close()

        code = self.get_code(receivedMessage)
        body = self.get_body(receivedMessage)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        info = self.parse_url(url)
        self.connect(info["hostname"], info["port"])
        request = f'POST {info["path"]} HTTP/1.0\r\nHost: {info["hostname"]}:{info["port"]}\r\nConnection: Close\r\n'
        if args:
            assembledArgs = self.assemble_args(args)
            request += "Content-Type: application/x-www-form-urlencoded\r\n"
            request += f'Content-Length: {len(assembledArgs.encode("utf-8"))}\r\n\r\n'
            request += assembledArgs + '\r\n'
        else:
            request += "Content-Length: 0\r\n"
        request += '\r\n'

        print(request)

        self.sendall(request)

        receivedMessage = self.recvall(self.socket)
        self.close()

        code = self.get_code(receivedMessage)
        body = self.get_body(receivedMessage)
        return HTTPResponse(code, body)

    def assemble_args(self, args):
        assembledArgs = ""
        for key, val in args.items():
            assembledArgs += key + '=' + val + '&'
        return assembledArgs[0:len(assembledArgs)-1]


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
