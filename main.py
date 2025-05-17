from src.url.url import URL
from src.url.view_source import ViewSourceURL

def show(body: str, is_view_source: bool = False):
    if is_view_source:
        print(body)
    else:
        in_tag = False
        i = 0
        while i < len(body):
            if body[i:i+4] == "&lt;":
                print("<", end="")
                i += 4
            elif body[i:i+4] == "&gt;":
                print(">", end="")
                i += 4
            elif body[i] == "<":
                in_tag = True
                i += 1
            elif body[i] == ">":
                in_tag = False
                i += 1
            elif not in_tag:
                print(body[i], end="")
                i += 1
            else:
                i += 1

def load(url: URL):
    body = url.request()
    show(body, isinstance(url, ViewSourceURL))

if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    if url.startswith("view-source:"):
        load(ViewSourceURL(url))
    else:
        load(URL(sys.argv[1]))