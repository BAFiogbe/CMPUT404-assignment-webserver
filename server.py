#Import libraries
import socketserver, os
#import mimetypes 
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

        # Split the request line into its components
        data = request_data[0].split(" ")
        r_command = data[0]  # HTTP Method (GET, POST, HEAD, etc.)
        r_url =  data[1]     # Requested URL
        r_http = data[2]     # HTTP version

        if r_command != "GET":
            output = r_http + " 405 Method Not Allowed\r\n" + "\r\n"
            self.request.send(output.encode("utf-8"))
            return
        
        if '..' in r_url:  # handle home directory
            self.request.sendall(bytearray(f'HTTP/1.0 404 NOT FOUND\r\n\n', 'utf-8'))

        else:
            # Handling redirection for missing trailing slashes.
            if (r_url[-5:] != ".html" and r_url[-1] != "/" and r_url[-4:] != ".css" and r_url[-3:] != ".js"):
                output = r_http + " 301 Moved Permanently\r\n" + "Location: " + r_url + "/\r\n"
                self.request.send(output.encode("utf-8"))
                return

            if r_url[-4:] == ".css":
                check_css = True

            path = os.getcwd() + "/www" + r_url

            # Check if path is a directory
            if os.path.isdir(path):
                # Try to use a default file such as index.html
                path = os.path.join(path, 'index.html')
                if not os.path.exists(path):
                    # Return a 404 if index.html does not exist
                    output = r_http + " 404 Not Found\r\n" + "\r\n"
                    self.request.send(output.encode("utf-8"))
                    return

            try:
                file = open(path, "rb")
                html_data = file.read()
                file.close()
            except FileNotFoundError:
                output = r_http + " 404 Not Found\r\n" + "\r\n"
                self.request.send(output.encode("utf-8"))
                return

            if check_css:
                output = r_http + " 200 OK\r\n" + "Content-Type: text/css\r\n" + "\r\n"
            else:
                output = r_http + " 200 OK\r\n" + "Content-Type: text/html\r\n" + "\r\n"
            self.request.send(output.encode("utf-8"))
            self.request.sendall(html_data)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    server.serve_forever()
