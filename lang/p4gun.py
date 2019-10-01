from os.path import isfile
from urllib3 import PoolManager
from html2text import html2text
from textract import process

def slurp(s):
    string = ""
    if isfile(s):
        string = process(s)
    else:
        http = PoolManager()
        html = str(http.request('GET', s).data)
        string = html2text(html)
    string = str(string)
    return string

if __name__ == '__main__':
    sys = __import__("sys")
    if len(sys.argv) > 1:
        print(slurp(sys.argv[1]))
