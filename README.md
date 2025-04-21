# RivaBrowser

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/nukri060/simple-web-browser/actions/workflows/python-package.yml/badge.svg)](https://github.com/nukri060/simple-web-browser/actions)
[![Code Coverage](https://codecov.io/gh/nukri060/simple-web-browser/branch/main/graph/badge.svg)](https://codecov.io/gh/nukri060/simple-web-browser)

A lightweight, terminal-based web browser written in Python, designed for educational purposes and web protocol exploration.

## ✨ Features

- **Modern Protocol Support**
  - HTTP/1.1 and HTTP/2 with automatic protocol detection
  - SSL/TLS encryption
  - Connection pooling and caching
  - ALPN negotiation

- **User Experience**
  - Interactive command interface
  - Smart content preview
  - Automatic encoding detection
  - Comprehensive history management
  - Detailed performance metrics

- **URL Scheme Support**
  - `http://` and `https://`
  - `file://` for local files
  - `view-source:` for source viewing
  - `data:` URLs
  - HTTP Basic Authentication

- **Developer Features**
  - Modular architecture
  - Type-safe implementation
  - Comprehensive test coverage
  - Detailed logging system
  - Extensible design

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install rivabrowser

# Or install from source
git clone https://github.com/nukri060/simple-web-browser.git
cd simple-web-browser
pip install -e .
```

### Basic Usage

```bash
# Open a website
riva-browser "https://example.com"

# View page source
riva-browser "view-source:https://example.com"

# Open local file
riva-browser "file:///path/to/file.html"
```

### Interactive Commands

While browsing, use these commands:
- `!history` - Show browsing history
- `!save` - Save current page
- `!links` - Extract and display links
- `!stats` - Show cache statistics
- `!clear` - Clear terminal
- `!help` - Show available commands
- `!exit` - Quit browser

## 📚 Documentation

- **[User Guide](guide.md)** - Detailed usage instructions
- **[API Reference](docs/api.md)** - Complete API documentation
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history

## 🏗 Project Structure

```
RivaBrowser/
├── riva/                  # Core package
│   ├── __init__.py       # Package definition
│   ├── cache.py          # Connection caching
│   ├── http2.py          # HTTP/2 implementation
│   ├── url.py            # URL handling
│   ├── utils.py          # Utilities
│   └── cli.py            # Command line interface
├── tests/                # Test suite
├── docs/                 # Documentation
├── examples/             # Usage examples
└── requirements.txt      # Dependencies
```

## 🛠 Development

### Setting Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=riva

# Run specific test file
pytest tests/test_http2.py
```

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for all new code
- Document all public APIs
- Write tests for new features

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for details on:
- How to report bugs
- How to propose features
- Code style guidelines
- Commit message format
- Pull request process

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by educational browser projects
- Built with Python's standard library
- Uses [h2](https://github.com/python-hyper/h2) for HTTP/2 support