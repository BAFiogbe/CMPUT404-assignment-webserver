#  coding: utf-8 
import socketserver, os, mimetypes 



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
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        if not self.data:
            return
        if len(self.data) < 3:
            output = "HTTP/1.1 400 Bad Request\r\n\r\n"
            self.request.sendall(output.encode("utf-8"))
            return

        request = self.data.decode("utf-8")
        request_data = request.splitlines()  

        check_css = False
        check_js = False

        data = request_data[0].split(" ")
        r_command = data[0]
        r_url =  data[1]
        r_http = data[2]


        if r_command != "GET":
            output = r_http + " 405 Method Not Allowed\r\n" + "\r\n"
            self.request.send(output.encode("utf-8"))


        else:
            if(r_url[-5:] != ".html" and r_url[-1] != "/" and r_url[-4:] != ".css"):
                output = r_http + " 301 Moved Permanently\r\n" + "Location: " + r_url + "/\r\n"
                self.request.send(output.encode("utf-8"))
            if r_url[-1:] == ".js":
                r_url = r_url + "index.html"
            if r_url[-4:] == ".css":
                check_css = True
            if r_url[-4:] == ".js":
                check_js = True

            try:
                file = open(os.getcwd() + "/www" + r_url, "rb")
                html_data = file.read()
                file.close()

            except FileNotFoundError:
                output = r_http + " 404 Not Found\r\n" + "\r\n"
                self.request.send(output.encode("utf-8"))
                
            else:
                

                if check_css:
                    output = r_http + " 200 OK\r\n" + "Content-Type: text/css\r\n" + "\r\n"
                else:
                    output = r_http + " 200 OK\r\n" + "Content-Type: text/html\r\n" + "\r\n"
                self.request.send(output.encode("utf-8"))
                self.request.sendall(html_data)

        #print ("Got a request of: %s\n" % self.data)
        self.request.sendall(bytearray("OK",'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
