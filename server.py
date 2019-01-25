#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    allowedMethods = "GET"

    def handle(self):

        try:
            self.data = self.request.recv(1024).strip()
            requestData = self.data.decode("utf-8")
            requestData = requestData.split(" ")
            httpRequestType = requestData[0]   
            if(httpRequestType == self.allowedMethods):
                requestedURLFile = requestData[1]

                if(requestedURLFile == "/"):
                    htmlFP = open("./www/index.html")
                    indexHTML = htmlFP.read()
                    httpHeader = "HTTP/1.1 200 OK \nContent-Type: text/html\n\n" + indexHTML +"\n"
                    self.request.sendall(httpHeader.encode())
                    return
                else:
                    isValid, path = self.getValidFilePath(requestedURLFile)
                    if(isValid == "moved"):
                        getHost = requestData[3].split("\r\n")
                        host = getHost[0]
                        redirectURL = requestedURLFile + "/"
                        httpHeader = "HTTP/1.1 301 Moved Permanently \nLocation: {}\n\n".format(redirectURL)
                        self.request.sendall(httpHeader.encode())

                    elif(isValid == False):
                        httpHeader = "HTTP/1.1 404 File does not exist\n\n"
                        self.request.sendall(httpHeader.encode())
                    
                    elif (isValid == True):
                        fp = open(path)
                        fileToSend = fp.read()
                        httpHeader = ""
                        
                        if "html" in path:
                            httpHeader = "HTTP/1.1 200 OK \nContent-Type: text/html\n\n" + fileToSend +"\n"
                        
                        elif "css" in path:
                            httpHeader = "HTTP/1.1 200 OK \nContent-Type: text/css\n\n" + fileToSend +"\n"
                        else: #if the file is not in html or css
                            httpHeader = "HTTP/1.1 404 File does not exist\n\n"
                       
                        self.request.sendall(httpHeader.encode())

            else:
                httpHeader = "HTTP/1.1 405 Method not allowed\n\n"
                self.request.sendall(httpHeader.encode())
        except():
            print("Error")

    def getValidFilePath(self, requestedFileOrDir):
            cwd = os.getcwd()
            getPath = cwd + "/www" + requestedFileOrDir
            resolvePath = os.path.normpath(getPath)

            if(cwd not in resolvePath):
                return (False, None)

            isValidFile = os.path.isfile(getPath)
            isValidFldr = os.path.isdir(getPath)
            if(isValidFile):
                return (True, getPath)
            elif(isValidFldr):
                if(getPath[-1] != "/"):
                    return ("moved", requestedFileOrDir + "/")
                else:
                    return (True, getPath + "index.html")
            else:
                return (False, None)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
