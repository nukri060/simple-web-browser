# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced HTTP/2 implementation with improved error handling and type safety
  - Comprehensive documentation and type hints
  - Custom exception hierarchy for better error handling
  - Context managers for connection management
  - Improved SSL/TLS configuration and ALPN negotiation
  - Input validation and security checks
  - Enhanced test coverage with new test cases
  - Fixed resource leaks and connection state issues

- Improved utils module with enhanced functionality
  - Added comprehensive module documentation and type hints
  - Introduced LinkInfo dataclass for structured link data
  - Enhanced HTML processing with sanitization and link extraction
  - Improved error handling and logging throughout
  - Added support for relative URL resolution with base URLs
  - Enhanced content display with better formatting and error handling
  - Added doctest support for documentation examples
  - Improved test coverage with new test cases

### Changed
- Updated error handling in HTTP/2 implementation
- Improved connection cleanup and resource management
- Enhanced request/response handling with better validation

### Fixed
- Fixed potential resource leaks in HTTP/2 connections
- Addressed missing protocol verifications
- Fixed improper handling of pseudo-headers
- Improved error handling in HTML processing
- Fixed URL resolution issues with relative links

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