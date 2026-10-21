"""Deliberately flawed synthetic web fixture. Bind only to IPv4 loopback."""
import argparse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3
from urllib.parse import parse_qs, urlsplit


def handle(path, authorization='', secure=False):
    parsed = urlsplit(path)
    query = parse_qs(parsed.query, keep_blank_values=True)
    if len(path) > 4096:
        return 414, 'text/plain', 'Request too long'
    if parsed.path == '/health':
        return 200, 'application/json', json.dumps({'fixture':'assessment-workbench', 'secure':secure})
    if parsed.path == '/orders':
        identity = {'Bearer lab-a':'a','Bearer lab-b':'b'}.get(authorization)
        if identity is None:
            return 401, 'application/json', '{"error":"synthetic token required"}'
        order = query.get('id',[''])[0]
        objects = {'1001':{'id':'1001','owner':'a','item':'synthetic notebook'},'2001':{'id':'2001','owner':'b','item':'synthetic pen'}}
        if order not in objects or (secure and objects[order]['owner'] != identity):
            return 404, 'application/json', '{"error":"not found"}'
        return 200, 'application/json', json.dumps(objects[order])
    if parsed.path == '/search':
        value = query.get('id',['1'])[0]
        with sqlite3.connect(':memory:') as connection:
            connection.execute('CREATE TABLE products(id INTEGER, name TEXT)')
            connection.executemany('INSERT INTO products VALUES(?,?)',[(1,'synthetic notebook'),(2,'synthetic pen')])
            try:
                if secure:
                    if not value.isascii() or not value.isdigit() or len(value)>6:
                        return 400, 'application/json', '{"error":"numeric id required"}'
                    rows = connection.execute('SELECT id,name FROM products WHERE id=?',(int(value),)).fetchall()
                else:
                    # Intentionally vulnerable: fixture database contains only two
                    # synthetic rows and is discarded after every request.
                    rows = connection.execute('SELECT id,name FROM products WHERE id='+value).fetchall()
            except sqlite3.Error:
                return 400, 'application/json', '{"error":"fixture query rejected"}'
        return 200, 'application/json', json.dumps(rows)
    if parsed.path == '/echo':
        value = query.get('q',[''])[0]
        return 200, 'text/html', '<!doctype html><title>Owned lab echo</title><main>'+(html.escape(value) if secure else value)+'</main>'
    return 404, 'application/json', '{"error":"fixture route does not exist"}'


def serve(port, secure):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            host = self.headers.get('Host','')
            if host != f'127.0.0.1:{self.server.server_port}':
                self.send_error(400, 'Use the exact loopback host')
                return
            status, mime, body = handle(self.path,self.headers.get('Authorization',''),secure)
            raw=body.encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type',mime+'; charset=utf-8')
            self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers()
            self.wfile.write(raw)
        def log_message(self,*args):
            pass  # Never write bearer tokens or payloads to implicit access logs.
    server = ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print(f'Synthetic fixture on http://127.0.0.1:{server.server_port}; secure={secure}',flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--secure',action='store_true')
    args=parser.parse_args()
    if not 1024<=args.port<=65535:
        parser.error('Use an unprivileged port from 1024 through 65535')
    serve(args.port,args.secure)
