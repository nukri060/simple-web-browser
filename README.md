# RivaBrowser  
**From Terminal to Tomorrow: A Browser Engine in Evolution**  
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue)](https://python.org) 
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

<img src="assets/protocol-flow.gif" width="600" alt="Protocol visualization demo">

## Where Command Line Meets Browser Innovation

RivaBrowser is **a living project** that starts as a terminal-based web client but aspires to become a full educational browser platform. It's built for those who believe understanding the web shouldn't require reverse-engineering billion-dollar browsers.

```python
# Today's reality
from rivabrowser import request
response = request("https://example.com")  # Returns plain text

# Tomorrow's possibilities? Your call:
def render_modern_web(url):
    return WebGPU_engine(url)  # Maybe someday?

## ✨ Features

- Modern protocol support (HTTP/1.1, HTTPS)
- Connection caching for faster loading
- View page sources (`view-source:`)
- `data:` URL handling
- Local file browsing (`file://`)
- Modular architecture for easy extension
- SSL/TLS secure connections
- HTML5 parsing support

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/nukri060/simple-web-browser.git
cd RivaBrowser
pip install -e .
```

### Command Line Usage
```bash
riva "https://example.com"
```

### Python Module
```python
from riva import URL, load

# Advanced usage
url = URL("https://example.com")
response = url.request()

# Simple usage
load("https://example.com")
```

## 🌟 Supported URL Schemes
- `http://` / `https://`
- `file://` (local files)
- `view-source:`
- `data:text/html,`

## 🏗 Project Structure

```
RivaBrowser/
├── riva/                  # Core package
│   ├── __init__.py        # Package definition
│   ├── cache.py           # Connection manager
│   ├── url.py             # URL parsing/request handling
│   └── utils.py           # Utilities
├── tests/                 # Unit tests
├── main.py                # CLI entry point
└── requirements.txt       # Dependencies
```

## 🔧 Development

### Extending Functionality
```python
from riva import URL

class CustomURL(URL):
    def _handle_custom_scheme(self, url):
        """Implement custom URL scheme handling"""
        pass
```

### Running Tests
```bash
python -m unittest discover tests
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with ❤️ for open source</sub>
</div>
