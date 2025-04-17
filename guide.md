# RivaBrowser User Guide

## Introduction

RivaBrowser is a terminal-based web browser implemented in Python that provides a lightweight yet powerful way to browse the web. This guide will walk you through its installation, basic usage, and advanced features.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/nukri060/simple-web-browser.git
   ```

2. Navigate to the project directory:
   ```bash
   cd simple-web-browser
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Basic Usage

### Opening Web Pages

To browse a website, use the following command:
```bash
python -m riva "https://example.com"
```

The browser supports various URL schemes:
- HTTP/HTTPS URLs: `https://example.com`
- Local files: `file:///path/to/file.html`
- View source: `view-source:https://example.com`

### Command Line Options

RivaBrowser supports several command-line options:

```bash
python -m riva [URL] [OPTIONS]

Options:
  --timeout SECONDS     Set request timeout (default: 30)
  --user-agent STRING  Set custom User-Agent
  --log-file PATH     Specify log file location
  --version           Show version information
  --history           Display browsing history
```

## Interactive Commands

While browsing, you can use the following interactive commands:

| Command    | Description                                |
|------------|--------------------------------------------|
| !history   | Display your browsing history              |
| !save      | Save current page to saved_page.html       |
| !links     | Show all links on the current page         |
| !stats     | Display cache and performance statistics   |
| !clear     | Clear the terminal screen                  |
| !help      | Show available commands                    |
| !exit      | Exit the browser                          |

## Advanced Features

### Connection Caching

RivaBrowser implements connection caching to improve performance:
- Maintains a pool of active connections
- Reuses connections for the same host
- Automatically manages connection lifecycle

### Performance Statistics

View detailed statistics about your browsing session using the !stats command:
```
Total Requests: 100
Cache Hits: 75
Cache Misses: 25
Hit Rate: 75.0%
Active Connections: 10
Max Pool Size: 20

Performance Metrics:
- Average Response Time: 0.45 sec
- Total Data Transferred: 1.2 MB
```

### Error Handling

RivaBrowser provides clear error messages for common issues:
- Connection timeouts
- DNS resolution failures
- SSL/TLS errors
- HTTP error codes

## Troubleshooting

### Common Issues

1. Connection Timeout
   - Check your internet connection
   - Try increasing the timeout value: `--timeout 60`

2. SSL Certificate Errors
   - Verify the website's SSL certificate is valid
   - Check your system's CA certificates

3. Permission Denied
   - Ensure you have read/write permissions for log files
   - Check file system permissions for local file access

### Getting Help

If you encounter issues:
1. Check the error message in the terminal
2. Review the log file if logging is enabled
3. Create an issue on the GitHub repository with:
   - Error message
   - Command used
   - System information

## Best Practices

1. Use appropriate timeouts for your network conditions
2. Enable logging for debugging
3. Regularly clear browser history and cache if needed
4. Use view-source for investigating web pages
5. Save important pages locally using !save

## Technical Details

### Architecture

RivaBrowser is built with a modular architecture:
- URL handling and parsing (url.py)
- Connection management (cache.py)
- Content display (utils.py)
- Command-line interface (cli.py)

### Security Considerations

- HTTPS connections are verified using system CA certificates
- Local file access is restricted to readable files
- User credentials are never stored
- Temporary files are properly cleaned up

## Contributing

For development and contribution guidelines, please refer to CONTRIBUTING.md in the repository.
