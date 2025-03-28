# RivaBrowser

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<img src="assets/logo.png" width="150" align="right">

RivaBrowser is a lightweight console-based web browser written in Python, designed as an educational platform for understanding web protocols and browser internals.

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
git clone https://github.com/yourusername/RivaBrowser.git
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
