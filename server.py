#!/usr/bin/env python3
"""Simple CORS proxy server for Helsinki Energy & Weather app"""

import http.server
import socketserver
import urllib.request
import urllib.error
import json

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Proxy electricity API
        if self.path.startswith('/api/electricity'):
            try:
                url = 'https://dashboard.elering.ee/api/nps/price' + self.path[self.path.find('?'):]
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = response.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(data)
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
                return

        # Proxy weather API
        if self.path.startswith('/api/weather'):
            try:
                params = self.path[self.path.find('?'):]
                url = f'https://api.open-meteo.com/v1/forecast{params}'
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = response.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(data)
                return
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
                return

        # Serve static files
        super().do_GET()

if __name__ == '__main__':
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        print(f'Serving at http://localhost:{PORT}')
        httpd.serve_forever()
