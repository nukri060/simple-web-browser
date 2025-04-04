import os
import time
import colorama
from colorama import Fore, Style
import argparse
from datetime import datetime
from .url import URL
from .cache import connection_cache
from .utils import show, load, print_links
import logging
import sys
from typing import Optional

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
        except Exception as e:
            logging.error(f"History add failed: {e}")

    def show_history(self) -> None:
        """Safely display history with encoding fallback"""
        try:
            with open(self.history_file, 'rb') as f:
                content = f.read()
                try:
                    decoded = content.decode('utf-8')
                except UnicodeDecodeError:
                    decoded = content.decode('latin-1', errors='replace')
                show(Fore.MAGENTA + "\nBrowsing History:")
                show(decoded)
        except FileNotFoundError:
            show(Fore.YELLOW + "No history found")
        except Exception as e:
            show(Fore.RED + f"Error reading history: {str(e)}")

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

def main() -> None:
    args = parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        filename=args.log_file,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    history = HistoryManager()
    print_header()
    
    # Set timeout from CLI
    connection_cache.timeout = args.timeout
    
    if args.history:
        history.show_history()
        return
    
    last_content: Optional[str] = None
    
    try:
        # Direct URL mode
        if args.url:
            try:
                start_time = time.time()
                show(Fore.YELLOW + f"\nLoading: {args.url}")
                
                url_obj = URL(args.url, user_agent=args.user_agent)
                content = url_obj.request()
                last_content = content
                
                show(Fore.GREEN + "\n[Content Preview]")
                show(content[:500] + ("..." if len(content) > 500 else ""))
                
                load_time = time.time() - start_time
                show(Fore.CYAN + f"\nLoaded in {load_time:.2f} sec | "
                    f"Size: {len(content)} bytes")
                
                history.add(args.url, "SUCCESS")
                if args.verbose:
                    connection_cache.print_stats()
            except Exception as e:
                logging.error(f"Failed to load {args.url}: {e}")
                show(Fore.RED + f"Error: {str(e)}")
                history.add(args.url, f"ERROR: {str(e)}")
            return
        
        # Interactive mode
        while True:
            try:
                user_input = input(Fore.BLUE + "\n[riva] " + Style.RESET_ALL).strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() == '!help':
                    print_help()
                    continue
                    
                if user_input.lower() == '!clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print_header()
                    continue
                    
                if user_input.lower() == '!stats':
                    connection_cache.print_stats()
                    continue
                    
                if user_input.lower() == '!links':
                    if last_content:
                        print_links(last_content)
                    else:
                        show(Fore.RED + "No page loaded yet!")
                    continue
                    
                if user_input.lower() == '!history':
                    history.show_history()
                    continue
                    
                if user_input.lower() == '!save':
                    if last_content:
                        with open('saved_page.html', 'w', encoding='utf-8') as f:
                            f.write(last_content)
                        show(Fore.GREEN + "Page saved to saved_page.html")
                    else:
                        show(Fore.RED + "No content to save!")
                    continue
                    
                if user_input.lower() == '!exit':
                    show(Fore.MAGENTA + "\nGoodbye!")
                    break
                    
                # Process URL
                try:
                    start_time = time.time()
                    show(Fore.YELLOW + f"\nLoading: {user_input}")
                    
                    url_obj = URL(user_input, user_agent=args.user_agent)
                    content = url_obj.request()
                    last_content = content
                    
                    show(Fore.GREEN + "\n[Content Preview]")
                    show(content[:500] + ("..." if len(content) > 500 else ""))
                    
                    load_time = time.time() - start_time
                    show(Fore.CYAN + f"\nLoaded in {load_time:.2f} sec | "
                        f"Size: {len(content)} bytes")
                    
                    history.add(user_input, "SUCCESS")
                except Exception as e:
                    logging.error(f"Failed to load {user_input}: {e}")
                    show(Fore.RED + f"\nError: {str(e)}")
                    history.add(user_input, f"ERROR: {str(e)}")
                    show(Fore.YELLOW + "Type !help for available commands")
                    
            except KeyboardInterrupt:
                show(Fore.YELLOW + "\nOperation cancelled")
                continue
                
    finally:
        connection_cache.close_all()
        logging.info("Browser session ended")
        show(Fore.YELLOW + "\nAll connections closed")

if __name__ == "__main__":
    main()