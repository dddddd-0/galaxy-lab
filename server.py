"""Local-only development server. python server.py [--host LAN_IP] [--port 8765]"""
import argparse
import json
from functools import lru_cache
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from model import catalog, system, ensemble

ROOT=Path(__file__).resolve().parent

@lru_cache(maxsize=4)
def cached_catalog(seed,n):
    return catalog(seed,n)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT/'web'),**kwargs)
    def do_GET(self):
        url=urlparse(self.path)
        if not url.path.startswith('/api/'):
            return super().do_GET()
        try:
            q=parse_qs(url.query)
            def integer(name,default,lo,hi):
                value=int(q.get(name,[default])[0])
                if not lo <= value <= hi: raise ValueError(f'{name} out of range')
                return value
            seed=integer('seed',42,0,2**32-1)
            if url.path=='/api/catalog': result=cached_catalog(seed,integer('n',12000,100,30000))
            elif url.path=='/api/system': result=system(integer('index',0,0,100000000000),seed)
            elif url.path=='/api/ensemble': result=ensemble(integer('n',1000,100,3000),integer('runs',8,2,16))
            else: self.send_error(404); return
            payload=json.dumps(result,ensure_ascii=False,allow_nan=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(payload)))
            self.send_header('Cache-Control','no-store')
            self.end_headers(); self.wfile.write(payload)
        except (ValueError,TypeError) as exc:
            self.send_error(400,str(exc))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=8765)
    a=p.parse_args()
    print(f'Galaxy Lab: http://{a.host}:{a.port}',flush=True)
    ThreadingHTTPServer((a.host,a.port),Handler).serve_forever()
