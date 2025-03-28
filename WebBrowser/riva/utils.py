def show(body):
    # Displaying the response body, replacing HTML entities with proper characters.
    if body.startswith("HTTP/") or body.startswith("File not found") or body.startswith("Path is a directory") or body.startswith("Permission denied") or body.startswith("Error reading file"):
        print(body)
        return
        
    in_tag = False
    i = 0
    n = len(body)
    while i < n:
        c = body[i]
        if c == "&":
            # Handling HTML entities like &lt; and &gt; for proper output.
            if body.startswith("&lt;", i):
                print("<", end="")
                i += 4
            elif body.startswith("&gt;", i):
                print(">", end="")
                i += 4
            else:
                print(c, end="")
                i += 1
        elif c == "<":
            in_tag = True
            i += 1
        elif c == ">":
            in_tag = False
            i += 1
        elif not in_tag:
            print(c, end="")
            i += 1
        else:
            i += 1

def load(url):
    # Requesting and displaying the body content of a given URL.
    body = url.request()
    show(body)