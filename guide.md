# RivaBrowser User Guide

## Introduction

RivaBrowser is a lightweight web browser engine that supports both HTTP/1.1 and HTTP/2 protocols. 
It's designed for developers and power users who need a simple yet powerful web client.

## Installation

```bash
# Install from PyPI
pip install rivabrowser

# Or install from source
git clone https://github.com/yourusername/rivabrowser.git
cd rivabrowser
pip install -e .
```

## Basic Usage

### Command Line Interface

```bash
# Open a website
python -m riva "https://example.com"

# View page source
python -m riva "view-source:https://example.com"

# Open local file
python -m riva "file:///path/to/file.html"
```

### Protocol Selection

RivaBrowser automatically detects the best protocol to use, but you can force a specific protocol:

```bash
# Force HTTP/2
python -m riva "https://example.com" --protocol http/2

# Force HTTP/1.1
python -m riva "https://example.com" --protocol http/1.1

# Auto-detect (default)
python -m riva "https://example.com" --protocol auto
```

### Advanced Options

```bash
# Custom timeout
python -m riva "https://example.com" --timeout 10

# Custom user agent
python -m riva "https://example.com" --user-agent "MyCustomBrowser/1.0"

# Log to file
python -m riva "https://example.com" --log-file browser.log

# Set log level
python -m riva "https://example.com" --log-level DEBUG
```

## Interactive Commands

While browsing, use these commands:

- `!history` - Show browsing history with timestamps
- `!save` - Save current page to `saved_page.html`
- `!links` - Extract and display links from current page
- `!stats` - Show detailed cache statistics and performance metrics
- `!clear` - Clear the terminal screen
- `!help` - Show available commands
- `!exit` - Quit the browser

## HTTP/2 Features

RivaBrowser supports HTTP/2 with the following features:

- Automatic protocol detection
- Connection multiplexing
- Header compression
- Server push support
- Stream prioritization

### Protocol Detection

RivaBrowser automatically detects if a server supports HTTP/2 using ALPN (Application-Layer Protocol Negotiation).
If HTTP/2 is not supported, it falls back to HTTP/1.1.

### Performance Optimization

HTTP/2 provides several performance benefits:

- Multiple requests over a single connection
- Header compression
- Server push support
- Stream prioritization

## Cache Management

RivaBrowser includes a sophisticated connection cache:

```python
from riva import ConnectionCache

# Create custom cache
cache = ConnectionCache(
    timeout=30.0,      # Connection timeout in seconds
    max_pool_size=10,  # Maximum number of cached connections
    enable_metrics=True # Enable performance metrics
)

# View cache statistics
cache.print_stats()
```

## Error Handling

RivaBrowser provides detailed error information:

- Connection timeouts
- Protocol negotiation failures
- SSL/TLS errors
- Invalid URLs
- Network errors

## Logging

Enable detailed logging to debug issues:

```bash
# Set log level
python -m riva "https://example.com" --log-level DEBUG

# Log to file
python -m riva "https://example.com" --log-file debug.log
```

## Security Features

- SSL/TLS support
- Certificate verification
- Secure protocol negotiation
- Connection timeout protection

## Troubleshooting

### Common Issues

1. **Protocol Negotiation Failed**
   - Check if server supports HTTP/2
   - Try forcing HTTP/1.1 with `--protocol http/1.1`

2. **Connection Timeout**
   - Increase timeout with `--timeout`
   - Check network connectivity

3. **SSL/TLS Errors**
   - Verify server certificate
   - Check system time

### Getting Help

- Check the [documentation](https://github.com/yourusername/rivabrowser/wiki)
- Open an [issue](https://github.com/yourusername/rivabrowser/issues)
- Join our [Discord](https://discord.gg/your-server)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License. See [LICENSE](LICENSE) for details.
