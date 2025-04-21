# RivaBrowser Examples

This directory contains example scripts demonstrating various features of RivaBrowser.

## Basic Usage

[`basic_usage.py`](basic_usage.py) demonstrates common use cases:
- Making simple requests
- Using HTTP/2
- Connection caching
- Link extraction

Run it with:
```bash
python examples/basic_usage.py
```

## Advanced Usage

[`advanced.py`](advanced.py) shows more complex scenarios:
- Custom URL schemes
- Performance benchmarking
- Error handling
- Advanced caching features

Run it with:
```bash
python examples/advanced.py
```

## Example Output

### Basic Usage
```
Basic Request Example:
[Content from example.com]

HTTP/2 Example:
Status: 200
[Content from example.com]

Cache Example:
[Content preview]
Cache hits: 2
Cache misses: 1

Link Extraction Example:
Found 5 links
```

### Advanced Usage
```
Benchmark Example:
Standard requests: 1.23s
HTTP/2 requests: 0.45s
Improvement: 63.4%

Custom Scheme Example:
Custom scheme handled: custom://example

Error Handling Example:
URL Error: Invalid URL format
HTTP/2 Error: Connection failed

Advanced Cache Example:
Cache Statistics:
Total Requests: 3
Cache Hits: 2
Cache Misses: 1
Hit Rate: 66.7%
Average Connection Lifetime: 45.2s
```

## Creating Your Own Examples

Feel free to use these examples as a starting point for your own scripts. The examples demonstrate:
- Proper error handling
- Resource cleanup
- Type hints
- Documentation
- Best practices

For more information, see the [main documentation](../README.md). 