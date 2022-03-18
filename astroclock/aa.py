import subprocess as sp
import datetime
import re
import json
from wsgiref.simple_server import make_server

import os
newcd = __file__.rpartition('/')[0]
os.chdir(newcd)

print(os.path.abspath('.'))

class Alnamac:
    def __init__(self):
        pass

    def calculate(self, when: datetime.datetime, body: int) -> str:
        p = sp.Popen(['/usr/bin/aa'], stdin=sp.PIPE, stdout=sp.PIPE)
        si = "{}\n{}\n{}\n{}\n{}\n{}\n1\n1\n{}\n".format(
            when.year, when.month, when.day,
            when.hour, when.minute, when.second,
            body
        )
        si = si.encode()
        so, _se = p.communicate(si)
        so = so.decode()
        return self.postproc(so)
    
    def postproc(self, in_str: str) -> dict:
        name = re.search("\n +(.*?)\n\n", in_str)
        rises = re.search("\nrises (.*)\n", in_str)
        sets = re.search("\nsets (.*)\n", in_str)
        return {
            "name": name.group(1),
            "rises": self.parse_time(rises.group(1)),
            "sets": self.parse_time(sets.group(1))
        }

    def parse_time(self, in_time: str) -> datetime.datetime:
        pat = "^([0-9]+) ([A-Z][a-z]+) ([0-9]+) [A-Z][a-z]+.*?([0-9]+)h ([0-9]+)m ([0-9.]+)s"
        res = re.match(pat, in_time)
        if res is None:
            return None
        year, month, day, hour, minute, second = res.groups()
        year = int(year)
        month_lut = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')
        month = [i for i, m in enumerate(month_lut) if month.startswith(m)][0]
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        second = float(second)
        millisecond = (second % 1) * 1e3
        millisecond = int(millisecond)
        second = int(second)
        return [year, month, day, hour, minute, second, millisecond]

def router(env, start_response):
    route = env['PATH_INFO']
    if route == "/aa":
        return app_aa(env, start_response)
    if route == "/":
        start_response("200 OK", [("Content-Type", "text/html")])
        return [open("index.html", "rb").read()]
    start_response("404 Not Found", [])
    return []

def app_aa(env, start_response):
    q = env['QUERY_STRING']
    q = q.split('&')
    q = [i.partition('=') for i in q]
    q = [(i[0], i[2]) for i in q if i[1] == '=']
    q = dict(q)
    body = q.get('body')    
    if body is None:
        body = [0, 3]
    if ',' in body:
        body = body.split(',')
        body = [int(b) for b in body]
    a = Alnamac()
    when = datetime.datetime.now()
    ress = {}
    for b in body:
        res = (a.calculate(when, b))
        ress[res["name"]] = res
        del res["name"]
    status = "200 OK"
    headers = [("Content-Type", "application/json")]
    start_response(status, headers)
    return [json.dumps(ress).encode()]

def dump_env(env, start_response):
    status = "200 OK"
    headers = [("Content-Type", "text/plain")]
    start_response(status, headers)
    return [str(env).encode()]

with make_server('127.0.0.1', 22000, router) as httpd:
    print("Web server started")
    httpd.serve_forever()

def test_main():
    a = Alnamac()
    now = datetime.datetime.now()
    print("now:", now)
    print("SUN")
    print(a.calculate(now, 0))
    print("MOON")
    print(a.calculate(now, 3))

if __name__ == "__main__":
    test_main()
