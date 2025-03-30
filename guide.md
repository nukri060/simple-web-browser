# Overview

RivaBrowser is a minimalistic browser designed for:
✔ Fetching web pages (HTTP/HTTPS)
✔ Reading local files (file://)
✔ Handling data: and view-source: URLs
✔ Reusing TCP connections (performance boost)

**Ideal for**:
- API testing
- Educational projects
- Quick local file viewing


# Quick 
```bash
# Clone repository
git clone https://github.com/nukri060/simple-web-browser.git

# Navigate to project directory
cd simple-web-browser/RivaBrowser

# Run the browser
python -m riva "https://example.com"
```

# Modules

### 1. cache.py
**Smart TCP connection caching**
- Thread-safe LRU cache (auto-closes stale connections)
- Background cleanup thread
- Metrics: hit/miss ratio, evictions

**Usage**:
```python
from .cache import connection_cache

# Get a cached connection
sock = connection_cache.get("example.com", 443, "https")
```

**Config** (**in** __init__.py):
```python
connection_cache = ConnectionCache(
    timeout=30.0,      # Close idle connections after 30s
    max_pool_size=5    # Max cached connections
)
```
### 2. url.py
| URL Type      | Example           | Features  |
| ------------- |:-------------:| -----:|
| HTTP/HTTPS     | https://example.com | Connection reuse |
| file://      | file:///data.txt      |   	Cross-platform path support |
| view-source: | view-source:http://...      |    Recursive fetching |
| data: | data:text/html,<h1>Hi      |    Instant rendering |

**Methods**:
```python
url = URL("https://example.com")
content = url.request()  # Returns response body
```
### 3. url.py

**Content utilities**
- show(body) – Cleans HTML (strips tags, decodes entities)
- load(url) – Fetches URL and prints formatted output

**Example**:
```python
from riva.utils import load
load("file:///notes.txt")  # Prints file content
```
### Use Cases

**1. Fetch a Web Page**
```python
from Riva.url import URL
print(URL("https://httpbin.org/get").request()[:200])  # First 200 chars
```
**2. View Page Source**
```python
from Riva.utils import load
load("view-source:https://example.com")
```

**3. Read Local Files**
```bash
python -m riva file:///README.md
```

### 🛠 For Developers
**Extending Functionality**
- **Add new URL schemes** (e.g., ftp://):
```python
class URL:
    def _request_ftp(self):
        # Your implementation here
```

- **Customize cache**:
```python
# In __init__.py
connection_cache = ConnectionCache(
    timeout=60.0,
    max_pool_size=10
```