#!/usr/bin/env python3
"""
Local Security Server for Exo-Suit V5.0
This server runs locally only with security measures to prevent external access.
"""

import http.server
import socketserver
import os
import sys
import ssl
from pathlib import Path

class SecureLocalServer(http.server.SimpleHTTPRequestHandler):
    """Secure local-only HTTP server with security headers and localhost binding."""
    
    def end_headers(self):
        # Security headers for local development
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Content-Security-Policy', "default-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data:;")
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Log only local access attempts
        if self.client_address[0] in ['127.0.0.1', 'localhost', '::1']:
            super().log_message(format, *args)
        else:
            # Block and log external access attempts
            print(f"🚨 BLOCKED EXTERNAL ACCESS ATTEMPT from {self.client_address[0]}:{self.client_address[1]}")
    
    def do_GET(self):
        # Only allow localhost access
        if self.client_address[0] not in ['127.0.0.1', 'localhost', '::1']:
            self.send_error(403, "Access Denied - Local Only")
            return
        
        # Serve files normally for localhost
        super().do_GET()

def start_secure_local_server(port=8000, bind_host='127.0.0.1'):
    """Start a secure local-only HTTP server."""
    
    # Ensure we're binding to localhost only
    if bind_host not in ['127.0.0.1', 'localhost', '::1']:
        print("🚨 SECURITY ERROR: Server must bind to localhost only!")
        print("   Allowed hosts: 127.0.0.1, localhost, ::1")
        sys.exit(1)
    
    # Create server with localhost binding
    with socketserver.TCPServer((bind_host, port), SecureLocalServer) as httpd:
        print(f"🔒 SECURE LOCAL SERVER STARTED")
        print(f"   Host: {bind_host}")
        print(f"   Port: {port}")
        print(f"   URL: http://{bind_host}:{port}")
        print(f"   Security: Localhost only, external access blocked")
        print(f"   Press Ctrl+C to stop")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start secure local server for Exo-Suit V5.0")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    
    args = parser.parse_args()
    
    # Validate host binding
    if args.host not in ['127.0.0.1', 'localhost', '::1']:
        print("🚨 SECURITY ERROR: Only localhost binding allowed!")
        print("   Use: 127.0.0.1, localhost, or ::1")
        sys.exit(1)
    
    start_secure_local_server(args.port, args.host)
