# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2024-04-17

### Added
- HTTP/2 protocol support with automatic detection
- Protocol selection via command line (`--protocol` flag)
- Enhanced connection pooling for HTTP/2
- Improved connection lifecycle management
- Detailed logging for protocol detection
- New dependencies: `h2` and `hyper` for HTTP/2 support

### Changed
- Connection cache now supports both HTTP/1.1 and HTTP/2
- Improved connection reuse efficiency
- Enhanced error handling for protocol-specific issues
- Updated documentation with HTTP/2 support details

### Fixed
- Connection timeout handling for long-running requests
- SSL/TLS handshake improvements
- Memory leaks in connection pool

## [1.2.2] - 2024-04-10

### Added
- Enhanced cache statistics with detailed performance metrics
- Improved error handling and user feedback
- Comprehensive logging system
- History management with file checks and permissions

### Changed
- Optimized connection caching algorithm
- Improved memory usage in cache management
- Enhanced error messages for better debugging

### Fixed
- Memory leak in connection pool
- Race condition in cache cleanup
- File permission issues in history management

## [1.2.1] - 2024-04-05

### Added
- HTML5 parsing support
- Smart content preview with title and first paragraph extraction
- Enhanced cache statistics
- Improved error handling

### Changed
- Updated URL parsing to handle more edge cases
- Improved content encoding detection
- Enhanced logging system

### Fixed
- Fixed encoding issues with international websites
- Resolved memory leaks in content parsing
- Fixed cache eviction policy

## [1.2.0] - 2024-04-01

### Added
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

### Changed
- Complete rewrite of the core engine
- Improved error handling
- Enhanced security features
- Better performance through connection pooling

### Fixed
- Various security vulnerabilities
- Memory leaks in connection handling
- Encoding issues with non-ASCII content