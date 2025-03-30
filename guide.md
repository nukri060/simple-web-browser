
# RivaBrowser Documentation

🌟 **What is RivaBrowser?**

RivaBrowser is a simple web browser built with Python. Think of it as a bicycle compared to a car - it gets you where you need to go, but with just the essentials.

### What can it do?

- Open regular websites (like https://google.com)
- Show local files on your computer (like file:///home/yourname/notes.txt)
- Let you see website code (like view-source:https://example.com)
- Remember connections to make loading faster

🛠️ **Getting Started**

### Installation

- Make sure you have Python 3.6 or newer
- Download the project:
    ```bash
    git clone https://github.com/nukri060/simple-web-browser.git
    cd simple-web-browser/RivaBrowser
    ```

### Running the Browser

To visit a website:
```bash
python -m riva "https://example.com"
```

To open a local file:
```bash
python -m riva "file:///home/yourname/document.txt"
```

📂 **How It Works (Simple Explanation)**

### The Three Main Parts:

1. **URL Handler** - Understands web addresses
   - Knows different types like http://, file://, etc.
   - Can fetch content from each type

2. **Connection Saver** - Makes loading faster
   - Remembers websites you've visited
   - Reuses connections when possible

3. **Content Cleaner** - Makes pages look nice
   - Removes messy code tags
   - Fixes special characters

🧩 **Main Components**

### 1. The Cache (cache.py)

This is like a memory box that helps the browser work faster.

**What it does:**
- Keeps connections to websites open for a while
- Automatically closes old connections
- Tracks what's working well

**Example code:**
```python
from riva.cache import connection_cache

# Get a saved connection
saved_connection = connection_cache.get("example.com", 443, "https")

# Store a connection for later
connection_cache.store("example.com", 443, "https", your_connection)
```

### 2. The URL Processor (url.py)

This is like the browser's address bar - it understands where you want to go.

**Types of addresses it knows:**
| Type             | Example                    | What It Does                |
| ---------------- |:--------------------------:| ---------------------------:|
| Regular Website  | https://example.com         | Gets the webpage             |
| Local File       | file:///document.txt        | Opens your computer files    |
| Page Source      | view-source:http://...      | Shows the website's code     |
| Data             | data:text/html,       | Shows special content       |

**How to use it:**
```python
from riva.url import URL

website = URL("https://example.com")
content = website.request()  # Gets the page
```

### 3. The Display Helper (utils.py)

This makes websites look nice in your terminal.

**What it does:**
- `show()` - Cleans up webpage code
- `load()` - Gets and shows a page in one step

**Example:**
```python
from riva.utils import load

load("file:///notes.txt")  # Opens and shows your file
```

💡 **Common Uses**

### 1. Checking a Website
```python
from riva.url import URL

page = URL("https://httpbin.org/get")
print(page.request()[:200])  # Shows first 200 characters
```

### 2. Viewing Website Code
```python
from riva.utils import load

load("view-source:https://example.com")
```

### 3. Reading Local Files
```bash
python -m riva "file:///home/yourname/notes.txt"
```

🛠 **For Developers**

### Adding New Features

Want to add support for ftp:// links? Here's how:

- Add to `url.py`:
```python
class URL:
    def _request_ftp(self):
        # Your code to handle FTP goes here
```

- Update the allowed schemes:
```python
SCHEME_PORTS = {
    # ... existing schemes ...
    'ftp': 21  # Add FTP support
}
```

### Changing Cache Settings

Want to keep connections longer?
```python
# In __init__.py
connection_cache = ConnectionCache(
    timeout=60.0,    # Keep connections for 1 minute
    max_pool_size=10  # Remember up to 10 connections
)
```

❓ **Need Help?**

If something isn't working:

- Check you're using Python 3.6+
- Make sure the URL is correct
- Try running with just `python -m Riva` first

Remember - this is a simple browser. It won't handle complex websites like modern browsers do!

📜 **License**

Free to use and modify (MIT License)
