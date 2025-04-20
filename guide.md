# RivaBrowser User Guide

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Protocol Support](#protocol-support)
- [Performance Optimization](#performance-optimization)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)
- [Contributing](#contributing)

## Introduction

RivaBrowser is a lightweight, terminal-based web browser written in Python. It's designed for:
- Developers who need a simple web client
- Users who want to understand web protocols
- Educational purposes and protocol exploration
- Automation and scripting tasks

### Key Features
- HTTP/1.1 and HTTP/2 support
- SSL/TLS encryption
- Connection pooling and caching
- Interactive command interface
- Comprehensive logging
- Extensible architecture

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (for source installation)

### Installation Methods

#### From PyPI (Recommended)
```bash
pip install rivabrowser
```

#### From Source
```bash
# Clone the repository
git clone https://github.com/nukri060/simple-web-browser.git
cd simple-web-browser

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install in development mode
pip install -e .
```

### Verifying Installation
```bash
riva-browser --version
```

## Getting Started

### First Run
```bash
# Open a website
riva-browser "https://example.com"

# View page source
riva-browser "view-source:https://example.com"

# Open local file
riva-browser "file:///path/to/file.html"
```

### Basic Commands
- `!help` - Show available commands
- `!exit` - Quit the browser
- `!clear` - Clear the terminal screen

## Basic Usage

### URL Schemes
RivaBrowser supports various URL schemes:
- `http://` and `https://` - Web pages
- `file://` - Local files
- `view-source:` - Page source code
- `data:` - Data URLs
- `http://user:pass@site.com` - Basic authentication

### Interactive Commands
While browsing, use these commands:
- `!history` - Show browsing history with timestamps
- `!save` - Save current page to `saved_page.html`
- `!links` - Extract and display links from current page
- `!stats` - Show detailed cache statistics
- `!clear` - Clear the terminal screen
- `!help` - Show available commands
- `!exit` - Quit the browser

### Command Line Options
```bash
# Protocol selection
riva-browser "https://example.com" --protocol http/2
riva-browser "https://example.com" --protocol http/1.1
riva-browser "https://example.com" --protocol auto

# Connection settings
riva-browser "https://example.com" --timeout 10
riva-browser "https://example.com" --user-agent "MyCustomBrowser/1.0"

# Logging
riva-browser "https://example.com" --log-file browser.log
riva-browser "https://example.com" --log-level DEBUG
```

## Advanced Features

### HTTP/2 Support
RivaBrowser supports HTTP/2 with:
- Automatic protocol detection
- Connection multiplexing
- Header compression
- Server push support
- Stream prioritization

### Connection Caching
```python
from riva.cache import ConnectionCache

# Create custom cache
cache = ConnectionCache(
    timeout=30.0,      # Connection timeout
    max_pool_size=10,  # Maximum cached connections
    enable_metrics=True # Performance tracking
)

# View cache statistics
stats = cache.get_stats()
print(f"Cache hits: {stats.hits}")
print(f"Cache misses: {stats.misses}")
print(f"Hit rate: {stats.hit_rate:.1%}")
```

### Custom URL Handling
```python
from riva import URL

class CustomURL(URL):
    def _handle_custom_scheme(self, url: str) -> str:
        if url.startswith("custom://"):
            return f"Custom scheme handled: {url}"
        return super()._handle_custom_scheme(url)
```

## Protocol Support

### HTTP/1.1
- Standard request/response model
- Connection keep-alive
- Chunked transfer encoding
- Basic authentication

### HTTP/2
- Binary framing layer
- Stream multiplexing
- Header compression (HPACK)
- Server push
- Stream prioritization

### Protocol Detection
RivaBrowser uses ALPN to detect HTTP/2 support:
1. Attempts HTTP/2 connection
2. Falls back to HTTP/1.1 if not supported
3. Reports protocol used in logs

## Performance Optimization

### Connection Pooling
- Reuses existing connections
- Reduces connection overhead
- Improves response times

### Caching Strategies
- LRU (Least Recently Used) cache
- Connection timeout management
- Automatic cleanup of stale connections

### HTTP/2 Benefits
- Reduced latency
- Better bandwidth utilization
- Improved page load times
- Lower server load

## Security

### SSL/TLS
- Certificate verification
- Protocol version negotiation
- Cipher suite selection
- SNI (Server Name Indication) support

### Security Features
- Connection timeout protection
- Input validation
- Secure protocol negotiation
- Error handling

### Best Practices
1. Always use HTTPS when available
2. Verify server certificates
3. Keep software updated
4. Use strong cipher suites

## Troubleshooting

### Common Issues

#### Protocol Negotiation Failed
```bash
# Try forcing HTTP/1.1
riva-browser "https://example.com" --protocol http/1.1

# Check server support
curl -I --http2 https://example.com
```

#### Connection Timeout
```bash
# Increase timeout
riva-browser "https://example.com" --timeout 30

# Check network connectivity
ping example.com
```

#### SSL/TLS Errors
```bash
# Verify certificate
openssl s_client -connect example.com:443

# Check system time
date
```

### Debugging
```bash
# Enable debug logging
riva-browser "https://example.com" --log-level DEBUG --log-file debug.log

# Check protocol detection
riva-browser "https://example.com" --protocol auto --log-level DEBUG
```

## API Reference

### Core Classes
- `URL` - URL handling and requests
- `HTTP2Connection` - HTTP/2 implementation
- `ConnectionCache` - Connection management
- `HistoryManager` - Browsing history

### Utility Functions
- `show()` - Display content
- `print_links()` - Extract and display links
- `load()` - Load content from URL

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- How to report bugs
- How to propose features
- Code style guidelines
- Pull request process

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Documentation](https://github.com/nukri060/simple-web-browser/wiki)
- [Issue Tracker](https://github.com/nukri060/simple-web-browser/issues)
- [Examples](examples/)
- [API Reference](docs/api.md)
