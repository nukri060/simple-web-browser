# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation for HTTP/2 module
- Type hints and dataclasses for better type safety
- Custom exception hierarchy for HTTP/2 errors
- Context managers for connection handling
- Input validation for host and port
- ALPN negotiation verification
- TCP_NODELAY optimization
- SSL certificate verification
- Stream reset handling
- Pseudo-header validation
- Improved test coverage

### Changed
- HTTP/2 connection error handling to use exceptions instead of return values
- Connection cleanup to ensure proper resource release
- Request/response handling to be more robust
- Test suite to match new error handling and features

### Fixed
- Potential resource leaks in connection handling
- Missing ALPN protocol verification
- Incomplete SSL configuration
- Improper handling of pseudo-headers
- Stream reset scenarios
- Connection state management 