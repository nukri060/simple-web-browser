# Changelog

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