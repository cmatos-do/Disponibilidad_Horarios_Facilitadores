import os
import sys
import subprocess
import time
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

PORT = 8000
DIRECTORY_TO_WATCH = 'horarios'

class AutoUpdateHandler(SimpleHTTPRequestHandler):
    """
    Subclass SimpleHTTPRequestHandler to serve index.html by default
    and auto-recompile PDF database if we detect file changes.
    """
    def do_GET(self):
        # Trigger directory check on every refresh/resource request as a lightweight watcher!
        try:
            check_and_recompile()
        except Exception as e:
            print(f"Error compiling PDFs on GET trigger: {e}")
        return super().do_GET()

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

# Track last modified times of files inside the watched directory
last_state = {}

def get_directory_state():
    state = {}
    if os.path.exists(DIRECTORY_TO_WATCH):
        for root, dirs, files in os.walk(DIRECTORY_TO_WATCH):
            for f in files:
                if f.lower().endswith('.pdf'):
                    path = os.path.join(root, f)
                    state[path] = os.path.getmtime(path)
    return state

def check_and_recompile(force=False):
    global last_state
    current_state = get_directory_state()

    if force or current_state != last_state:
        print("\n[AutoUpdater] Detected change in 'horarios/' directory. Regenerating database...")
        # Execute parse_pdf.py programmatically
        try:
            result = subprocess.run([sys.executable, 'parse_pdf.py'], capture_output=True, text=True)
            if result.returncode == 0:
                print("[AutoUpdater] Database updated successfully!")
            else:
                print(f"[AutoUpdater] Error recompiling: {result.stderr}")
        except Exception as e:
            print(f"[AutoUpdater] Failed to execute parse_pdf.py: {e}")

        last_state = current_state

def background_watcher():
    """
    Optional active background loop that sleeps and checks directory state.
    """
    print("[AutoWatcher] Active background directory watcher started.")
    while True:
        try:
            check_and_recompile()
        except Exception as e:
            print(f"[AutoWatcher] Error: {e}")
        time.sleep(1.5)

def main():
    # Force initial compile on launch
    check_and_recompile(force=True)

    # Start the active background watcher thread
    watcher_thread = threading.Thread(target=background_watcher, daemon=True)
    watcher_thread.start()

    # Start TCPServer to serve the files
    print(f"\n[Development Server] Starting server on http://localhost:{PORT}")
    try:
        with TCPServer(("", PORT), AutoUpdateHandler) as httpd:
            print(f"[Development Server] Serving dashboard. Press Ctrl+C to stop.")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping development server...")
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
