import os
import sys
import subprocess
import importlib.metadata
import time
import colorama
from colorama import Fore, Style
import argparse
from datetime import datetime
from .url import URL
from .cache import connection_cache
from .utils import show, load, print_links
import logging
from typing import Optional, Dict, Any
from .http2 import HTTP2Connection

# Initialize colorama
colorama.init(autoreset=True)

"""
RivaBrowser Main Module

Handles the browser's command line interface and interactive mode.
Supports both direct URL access and interactive sessions.

Key Features:
- Interactive command processing
- History management
- Content saving
- Connection statistics
"""

class HistoryManager:
    """Improved history tracker with encoding support"""
    def __init__(self, log_file: str = 'riva_history.log'):
        self.history_file = log_file
        self.entries = []
        self._ensure_history_file()
        
    def _ensure_history_file(self) -> None:
        """Ensure history file exists and is writable"""
        try:
            if not os.path.exists(self.history_file):
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    f.write("Timestamp | Status | URL\n")
                    f.write("-" * 80 + "\n")
            elif not os.access(self.history_file, os.W_OK):
                logging.warning(f"History file {self.history_file} is not writable")
        except Exception as e:
            logging.error(f"Failed to initialize history file: {e}")
        
    def add(self, url: str, status: str) -> None:
        """Add entry to history with error handling"""
        try:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'status': status
            }
            self.entries.append(entry)
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(f"{entry['timestamp']} | {status} | {url}\n")
            logging.info(f"Added history entry: {url} ({status})")
        except PermissionError:
            logging.error(f"Permission denied when writing to {self.history_file}")
            show(Fore.RED + "Warning: Could not save to history (permission denied)")
        except Exception as e:
            logging.error(f"History add failed: {e}")
            show(Fore.RED + f"Warning: Could not save to history: {str(e)}")

    def show_history(self) -> None:
        """Safely display history with encoding fallback"""
        try:
            if not os.path.exists(self.history_file):
                show(Fore.YELLOW + "No history found")
                return
                
            with open(self.history_file, 'rb') as f:
                content = f.read()
                try:
                    decoded = content.decode('utf-8')
                except UnicodeDecodeError:
                    decoded = content.decode('latin-1', errors='replace')
                show(Fore.MAGENTA + "\nBrowsing History:")
                show(decoded)
                logging.info("History displayed successfully")
        except FileNotFoundError:
            show(Fore.YELLOW + "No history found")
            logging.warning("History file not found")
        except Exception as e:
            show(Fore.RED + f"Error reading history: {str(e)}")
            logging.error(f"Failed to display history: {e}")

def check_dependencies() -> None:
    """Check and install required dependencies"""
    required_packages = {
        'requests': '2.31.0',
        'beautifulsoup4': '4.12.0',
        'urllib3': '2.0.0',
        'h2': '4.1.0',
        'hyper': '0.7.0',
        'pyOpenSSL': '23.3.0',
        'cryptography': '41.0.0',
        'colorama': '0.4.6',
        'rich': '13.7.0',
        'python-dateutil': '2.8.2',
        'chardet': '5.2.0',
        'idna': '3.6'
    }
    
    missing_packages = []
    outdated_packages = []
    
    for package, required_version in required_packages.items():
        try:
            installed_version = importlib.metadata.version(package)
            if importlib.metadata.version(package) < required_version:
                outdated_packages.append((package, installed_version, required_version))
        except importlib.metadata.PackageNotFoundError:
            missing_packages.append(package)
    
    if missing_packages or outdated_packages:
        print(Fore.YELLOW + "\nRivaBrowser needs to install or update some dependencies:")
        
        if missing_packages:
            print(Fore.CYAN + "\nMissing packages:")
            for package in missing_packages:
                print(f"  - {package}")
        
        if outdated_packages:
            print(Fore.CYAN + "\nOutdated packages:")
            for package, current, required in outdated_packages:
                print(f"  - {package} (current: {current}, required: {required})")
        
        print(Fore.YELLOW + "\nDo you want to install/update these packages? (y/n): ", end='')
        response = input().lower()
        
        if response == 'y':
            print(Fore.GREEN + "\nInstalling dependencies...")
            try:
                for package in missing_packages:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                
                for package, _, required in outdated_packages:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package}>={required}"])
                
                print(Fore.GREEN + "\nDependencies installed successfully!")
                time.sleep(1)  # Give user time to read the message
            except subprocess.CalledProcessError as e:
                print(Fore.RED + f"\nError installing dependencies: {str(e)}")
                sys.exit(1)
        else:
            print(Fore.RED + "\nCannot proceed without required dependencies.")
            sys.exit(1)

def parse_args():
    """Argument parser with version support"""
    parser = argparse.ArgumentParser(
        description='RivaBrowser - Lightweight Web Browser',
        epilog='Example: python -m Riva https://example.com --timeout 5'
    )
    parser.add_argument('url', nargs='?', help='URL to load (http://, file://)')
    parser.add_argument('--timeout', type=float, default=5.0, 
                      help='Connection timeout in seconds')
    parser.add_argument('--verbose', action='store_true',
                      help='Enable debug output')
    parser.add_argument('--history', action='store_true',
                      help='Show browsing history')
    parser.add_argument('--user-agent', type=str, default="RivaBrowser/1.0",
                      help='Custom User-Agent header')
    parser.add_argument('--log-file', type=str, default='riva_debug.log',
                      help='Path to debug log file')
    parser.add_argument('--version', action='version', 
                      version='RivaBrowser 1.2',
                      help='Show version and exit')
    parser.add_argument('--protocol', choices=['auto', 'http/1.1', 'http/2'],
                      default='auto', help='Force protocol version')
    parser.add_argument('--log-level', default='INFO',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                      help='Set logging level')
    return parser.parse_args()

def print_header(version: str = "1.2") -> None:
    """Print colorful header"""
    show(Fore.CYAN + f"""
    ┌──────────────────────────────────────┐
    │         RivaBrowser v{version.ljust(8)}        │
    │  Lightweight Python Web Browser      │
    └──────────────────────────────────────┘
    """)

def print_help() -> None:
    """Print colored help menu"""
    show(Fore.YELLOW + "\nAvailable commands:")
    show(Fore.GREEN + "!help    - Show this help")
    show(Fore.GREEN + "!clear   - Clear screen")
    show(Fore.GREEN + "!stats   - Show cache statistics")
    show(Fore.GREEN + "!links   - Extract links from last page")
    show(Fore.GREEN + "!history - Show browsing history")
    show(Fore.GREEN + "!save    - Save current page to file")
    show(Fore.GREEN + "!exit    - Quit browser")
    show(Fore.YELLOW + "\nEnter URL to navigate (http://, file://, view-source:)")

def print_stats() -> None:
    """Print detailed cache statistics with formatting"""
    stats = connection_cache.get_stats()
    
    show(Fore.CYAN + "\nCache Statistics:")
    show(Fore.YELLOW + "┌──────────────────────────────────────┐")
    show(Fore.YELLOW + f"│ Total Requests: {stats['total_requests']:>20} │")
    show(Fore.YELLOW + f"│ Cache Hits: {stats['cache_hits']:>24} │")
    show(Fore.YELLOW + f"│ Cache Misses: {stats['cache_misses']:>22} │")
    show(Fore.YELLOW + f"│ Hit Rate: {stats['hit_rate']:>26.1%} │")
    show(Fore.YELLOW + f"│ Active Connections: {stats['active_connections']:>16} │")
    show(Fore.YELLOW + f"│ Max Pool Size: {stats['max_pool_size']:>21} │")
    show(Fore.YELLOW + "└──────────────────────────────────────┘")
    
    if stats['total_requests'] > 0:
        show(Fore.GREEN + f"\nPerformance Metrics:")
        show(Fore.YELLOW + f"Average Response Time: {stats['avg_response_time']:.2f} sec")
        show(Fore.YELLOW + f"Total Data Transferred: {stats['total_bytes'] / 1024:.1f} KB")
    
    logging.info("Cache statistics displayed")

def setup_logging(level: str = "INFO") -> None:
    """Configure logging"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def detect_protocol(url: str) -> str:
    """Detect protocol from URL"""
    if url.startswith(('http://', 'https://')):
        return url.split('://')[0]
    return 'http'  # Default to HTTP

def process_url(url: str, user_agent: str = "RivaBrowser/1.0") -> tuple[Optional[str], float]:
    """Process URL and return response data with load time"""
    start_time = time.time()
    try:
        protocol = detect_protocol(url)
        response = make_request(url, protocol)
        if response and isinstance(response, dict):
            load_time = time.time() - start_time
            return response.get('content', ''), load_time
        elif response and isinstance(response, str):
            load_time = time.time() - start_time
            return response, load_time
        return None, 0.0
    except Exception as e:
        logging.error(f"Error processing URL {url}: {str(e)}")
        return None, 0.0

def make_request(url: str, protocol: str = 'auto') -> Optional[Dict[str, Any]]:
    """Make HTTP request using appropriate protocol"""
    try:
        parsed_url = URL(url)
        
        if protocol == 'auto':
            protocol = detect_protocol(url)
            
        if protocol == 'http/2' and parsed_url.scheme == 'https':
            conn = HTTP2Connection(parsed_url.host, parsed_url.port)
            if not conn.connect():
                raise Exception("Failed to establish HTTP/2 connection")
                
            stream_id = conn.send_request(
                'GET',
                parsed_url.path,
                {'user-agent': 'RivaBrowser/1.0'}
            )
            
            if stream_id is None:
                raise Exception("Failed to send HTTP/2 request")
                
            _, data = conn.receive_response()
            if data is None:
                raise Exception("No response received")
                
            return {
                'status': 200,
                'headers': {},
                'content': data.decode('utf-8', errors='replace'),
                'protocol': 'http/2'
            }
        else:
            # Fallback to HTTP/1.1
            return parsed_url.request()
            
    except Exception as e:
        logging.error(f"Request failed: {str(e)}")
        return None

def display_content(content: str, load_time: float) -> None:
    """Display content with formatting and statistics"""
    show(Fore.GREEN + "\n[Content Preview]")
    
    # Try to detect if content is HTML
    if content.strip().lower().startswith('<!doctype html') or content.strip().lower().startswith('<html'):
        # For HTML, show title and first paragraph
        title_start = content.lower().find('<title>')
        title_end = content.lower().find('</title>')
        if title_start != -1 and title_end != -1:
            title = content[title_start + 7:title_end].strip()
            show(Fore.CYAN + f"Title: {title}")
        
        # Find first paragraph
        p_start = content.lower().find('<p>')
        p_end = content.lower().find('</p>')
        if p_start != -1 and p_end != -1:
            preview = content[p_start + 3:p_end].strip()
            show(preview[:500] + ("..." if len(preview) > 500 else ""))
        else:
            show(content[:500] + ("..." if len(content) > 500 else ""))
    else:
        # For non-HTML content, show first 500 chars
        show(content[:500] + ("..." if len(content) > 500 else ""))
    
    show(Fore.CYAN + f"\nLoaded in {load_time:.2f} sec | "
         f"Size: {len(content)} bytes")

def main() -> None:
    # Check dependencies first
    check_dependencies()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='RivaBrowser - A lightweight web browser')
    parser.add_argument('url', nargs='?', help='URL to open')
    parser.add_argument('--protocol', choices=['auto', 'http/1.1', 'http/2'],
                      default='auto', help='Force protocol version')
    parser.add_argument('--log-level', default='INFO',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                      help='Set logging level')
    parser.add_argument('--version', action='version', version='1.3.0')
    
    args = parser.parse_args()
    
    if not args.url:
        parser.print_help()
        sys.exit(1)
        
    setup_logging(args.log_level)
    
    response, load_time = process_url(args.url)
    if response:
        print(response)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()