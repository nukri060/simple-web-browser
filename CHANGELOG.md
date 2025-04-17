# Changelog

## [1.2.2] - 2025-04-17

### Added
- Enhanced error handling and logging in HistoryManager
- Improved cache statistics display with better formatting
- HTML content detection and smart preview
- Title extraction from HTML pages
- First paragraph extraction for better content preview
- Detailed performance metrics in statistics
- File existence and permission checks for history
- Better error messages for users

### Improved
- History file initialization and management
- Cache statistics visualization with ASCII art
- Content display with HTML-aware formatting
- URL processing with better error handling
- Logging system with more detailed information
- User feedback for common errors
- Code organization and modularity

### Changed
- Refactored URL processing into separate function
- Enhanced content display logic
- Improved statistics collection and display
- Better error handling throughout the application

## [1.2.1] - 2025-04-02

### Improved
- Case-insensitive HTML tag matching in strip_scripts()
- Additional URL scheme filtering (javascript:, mailto:)
- Minimum URL length validation (3+ characters)
- Cache logging now includes timestamps
- Better href attribute extraction with IGNORECASE flag

## [1.2.0] - 2025-03-31

### Added
- Interactive commands: `!history`, `!save`
- HTTP Basic Authentication support
- `--version` command line flag
- Automatic encoding detection

### Changed
- Improved URL parsing logic
- Enhanced error handling system
- Updated connection caching algorithm

### Fixed
- Unicode handling in history tracking
- File path handling on Windows
- SSL certificate verification