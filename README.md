# RivaBrowser

## From Terminal to Tomorrow: A Browser Engine in Evolution

![Protocol visualization demo](assets/protocol-flow.gif)

### Where Command Line Meets Browser Innovation

RivaBrowser is a living project that starts as a terminal-based web client but aspires to become a full educational browser platform. It's built for those who believe understanding the web shouldn't require reverse-engineering billion-dollar browsers.

## 🚀 Today's Reality

```python
from rivabrowser import request

response = request("https://example.com")  # Returns plain text
```

## 🔮 Tomorrow's Possibilities?

```python
def render_modern_web(url):
    return WebGPU_engine(url)  # Maybe someday?
```

## ✨ Features (v1.2.0)

- Modern protocol support: HTTP/1.1, HTTPS with SSL/TLS
- Connection caching for faster loading
- Interactive commands: `!history`, `!save`, `!links`, `!stats`
- URL scheme support:
  - `http://` / `https://`
  - `file://` (local files)
  - `view-source:` (view page sources)
  - `data:` URLs
- HTTP Basic Authentication (`user:pass@site.com`)
- Automatic encoding detection for international websites
- Modular architecture for easy extension
- HTML5 parsing support
- Cache statistics and performance metrics

## 🚀 Quick Start

### Installation

```bash
# Install directly from GitHub
pip install git+https://github.com/nukri060/simple-web-browser.git

# Or clone and install locally
git clone https://github.com/nukri060/simple-web-browser.git
cd simple-web-browser
pip install -e .
```

### Basic Usage

```bash
# Open a website
python -m riva "https://example.com"

# View page source
python -m riva "view-source:https://example.com"

# Open local file
python -m riva "file:///path/to/file.html"
```

### Advanced Options

```bash
# With custom settings
python -m riva "https://example.com" \
  --timeout 10 \
  --user-agent "MyCustomBrowser/1.0" \
  --log-file browser.log

# Show version
python -m riva --version

# View browsing history
python -m riva --history
```

## 🛠 Interactive Commands

While browsing, use these commands:

- `!history` - Show browsing history
- `!save` - Save current page to `saved_page.html`
- `!links` - Extract and display links from current page
- `!stats` - Show cache statistics

## 🏗 Project Structure

```
RivaBrowser/
├── riva/                  # Core package
│   ├── __init__.py        # Package definition
│   ├── cache.py           # Connection manager with LRU caching
│   ├── url.py             # URL parsing/request handling
│   ├── utils.py           # Content display utilities
│   └── cli.py             # Command line interface
├── tests/                 # Unit tests
├── main.py                # CLI entry point
└── requirements.txt       # Dependencies
```

## 🔧 For Developers

### Extending Functionality

```python
from riva import URL

class CustomURL(URL):
    def _handle_custom_scheme(self, url):
        """Implement custom URL scheme handling"""
        pass
```

### Cache Configuration

```python
from riva.cache import ConnectionCache

# Custom cache settings
custom_cache = ConnectionCache(
    timeout=120.0,      # 2 minute timeout
    max_pool_size=20,   # Store 20 connections
    enable_metrics=True # Track performance
)
```

### Running Tests

```bash
python -m unittest discover tests
```

## 🤝 Contributing

We welcome contributions! Please follow our guidelines:

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use type hints for all new code
- Keep functions small and focused
- Use [Conventional Commits](https://www.conventionalcommits.org/) format:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `chore:` for maintenance tasks

See `CONTRIBUTING.md` for details.

## 📜 License

MIT License. See `LICENSE` for details.

## 📚 Documentation

- **[Changelog](CHANGELOG.md)** - Version history and changes
- **[User Guide](docs/USER_GUIDE.md)** - Detailed usage instructions
