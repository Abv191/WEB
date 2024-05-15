from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import UDPServer, BaseRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import json
import threading
import socket

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/' or parsed_url.path == '/index':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif parsed_url.path == '/message.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('message.html', 'rb') as file:
                self.wfile.write(file.read())
        elif parsed_url.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('style.css', 'rb') as file:
                self.wfile.write(file.read())
        elif parsed_url.path == '/logo.png':
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            with open('logo.png', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('error.html', 'rb') as file:
                self.wfile.write(file.read())

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_params = parse_qs(post_data.decode('utf-8'))
            message = post_params.get('message', [''])[0]
            username = post_params.get('username', [''])[0]
            if message and username:
                message_data = {
                    'username': username,
                    'message': message
                }
                # Зберігання даних у файлі
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                with open('storage/data.json', 'a') as file:
                    json.dump({timestamp: message_data}, file, indent=2)
                    file.write('\n')

                # Відправка клієнту перенаправлення на сторінку message.html
                self.send_response(
                    303)  # 303 означає "See Other" (змінився URI, даних немає, новий запит може бути виконаний методом GET)
                self.send_header('Location', '/message.html')
                self.end_headers()
            else:
                self.send_response(400)
                self.end_headers()


class SocketHandler(BaseRequestHandler):
    def handle(self):
        data, _ = self.request
        message_data = json.loads(data.decode('utf-8'))
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        with open('storage/data.json', 'a') as file:
            json.dump({timestamp: message_data}, file, indent=2)
            file.write('\n')

def run_http_server():
    http_server = HTTPServer(('localhost', 3000), HTTPRequestHandler)
    http_server.serve_forever()

def run_socket_server():
    socket_server = UDPServer(('localhost', 5000), SocketHandler)
    socket_server.serve_forever()

if __name__ == "__main__":
    http_thread = threading.Thread(target=run_http_server)
    socket_thread = threading.Thread(target=run_socket_server)

    http_thread.start()
    socket_thread.start()

    http_thread.join()
    socket_thread.join()
