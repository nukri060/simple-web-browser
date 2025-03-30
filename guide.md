
# RivaBrowser Documentation

## 🌟 What's New in v1.2.0?

- ✨ **Brand new** !history command - see where you've been
- 💾 **!save** command - keep pages for later
- 🔑 **HTTP Basic Auth** support (user:pass@site.com)
- 🌍 Better handling of international websites
- 📊 **Cache statistics** with !stats
- 🔍 Improved link extraction with !links

## What can it do now?

- Open websites (http://, https://)
- View local files (file://)
- See website code (view-source:)
- Handle special content (data:)
- Remember your browsing history
- Save pages to your computer
- Work with password-protected sites

## 🛠️ Getting Started

### Installation

#### Install directly from GitHub
```bash
pip install git+https://github.com/nukri060/simple-web-browser.git
```

#### Or clone and install locally
```bash
git clone https://github.com/nukri060/simple-web-browser.git
cd simple-web-browser
pip install -e .
```

### Running the Browser

#### Basic usage:
```bash
python -m riva "https://example.com"
```

#### Advanced options:
```bash
# With custom settings
python -m riva "https://example.com"   --timeout 10   --user-agent "MyCustomBrowser/1.0"   --log-file browser.log
```

## 📂 How It Works

### The Enhanced Components:

#### Smart URL Handler (url.py)

- New: Understands password-protected sites (user:pass@site.com)
- Better error handling
- Supports more website types

#### Supercharged Cache (cache.py)

- Tracks performance (hits/misses)
- Automatic cleanup
- Connection health checks

#### Content Display (utils.py)

- Improved text cleaning
- Better link extraction
- Support for multiple encodings

## 🧙‍♂️ Main Components (Updated)

### 1. The Cache System

#### New features:
```python
# Get cache statistics
from riva.cache import connection_cache
print(connection_cache.get_metrics())

# Sample output:
{
  'hits': 5,       # Successful cache uses
  'misses': 3,     # Cache misses
  'evictions': 1,  # Removed old connections
  'size': 2        # Current cached connections
}
```

### 2. URL Processing (New Features)

#### Handling password-protected sites:
```python
from riva.url import URL

# Access protected resource
protected = URL("http://user:pass@httpbin.org/basic-auth/user/pass")
content = protected.request()
```

### 3. Enhanced Display System

#### New commands:
```python
from riva.utils import show, print_links

# Show content with max length
show(very_long_content, max_length=500)

# Extract and display links
print_links(html_content)  # Shows first 15 links
```

## 💡 Common Uses (Updated)

### 1. Saving Important Pages
```bash
python -m riva "https://example.com"
[riva] !save  # Creates saved_page.html
```

### 2. Reviewing Your History
```bash
python -m riva --history  # Show all visited sites
```

### 3. Testing Website Connections

#### With debug output
```bash
python -m riva "https://example.com" --verbose
```

### 4. Extracting All Links
```bash
python -m riva "https://example.com"
[riva] !links  # Show all found links
```

## 🛠 For Developers

### Adding New Commands

Example: Adding `` command:
Edit `__main__.py`:
```python
if user_input.lower() == '!bookmark':
    save_to_bookmarks(last_url)
```

### Modifying Cache Behavior
```python
# Custom cache settings
custom_cache = ConnectionCache(
    timeout=120.0,      # 2 minute timeout
    max_pool_size=20,   # Store 20 connections
    enable_metrics=True # Track performance
)
```

## ❓ Troubleshooting

### Common issues:

- Encoding problems? Try `--verbose` to see details
- Connection issues? Adjust `--timeout` value
- Strange behavior? Check `--log-file`

## 📜 License

MIT License - Free to use and modify

## 💡 Tip: Run `python -m riva --version` to check your installed version!
