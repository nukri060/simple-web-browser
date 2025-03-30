import os
import time
import colorama
from colorama import Fore, Style
from .url import URL
from .cache import connection_cache
from .utils import show, load, print_links

# Initialize colorama
colorama.init(autoreset=True)

def print_header():
    """Print colorful header"""
    show(Fore.CYAN + """
    ┌──────────────────────────────────────┐
    │         RivaBrowser v1.1            │
    │  Lightweight Python Web Browser      │
    └──────────────────────────────────────┘
    """)

def print_help():
    """Print colored help menu"""
    show(Fore.YELLOW + "\nAvailable commands:")
    show(Fore.GREEN + "!help    - Show this help")
    show(Fore.GREEN + "!clear   - Clear screen")
    show(Fore.GREEN + "!stats   - Show cache statistics")
    show(Fore.GREEN + "!links   - Extract links from last page")
    show(Fore.GREEN + "!exit    - Quit browser")
    show(Fore.YELLOW + "\nEnter URL to navigate (http://, file://, view-source:)")

def main():
    print_header()
    last_content = None  # Store last fetched content
    
    try:
        while True:
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
                
            if user_input.lower() == '!exit':
                show(Fore.MAGENTA + "\nGoodbye!")
                break
                
            # Process URL
            try:
                start_time = time.time()
                show(Fore.YELLOW + f"\nLoading: {user_input}")
                
                url_obj = URL(user_input)
                content = url_obj.request()
                last_content = content
                
                show(Fore.GREEN + "\n[Content Preview]")
                show(content[:500] + ("..." if len(content) > 500 else ""))
                
                load_time = time.time() - start_time
                show(Fore.CYAN + f"\nLoaded in {load_time:.2f} sec | "
                    f"Size: {len(content)} bytes")
                
            except Exception as e:
                show(Fore.RED + f"\nError: {str(e)}")
                show(Fore.YELLOW + "Type !help for available commands")
                
    finally:
        connection_cache.close_all()
        show(Fore.YELLOW + "\nAll connections closed")

if __name__ == "__main__":
    main()