#!/usr/bin/env python3
"""
Remote Access Configuration for Exo-Suit V5.0
⚠️  WARNING: This enables external access - use only in trusted environments!
"""

import http.server
import socketserver
import os
import sys
import ssl
from pathlib import Path
import socket

class RemoteAccessServer(http.server.SimpleHTTPRequestHandler):
    """HTTP server with remote access capabilities and security warnings."""
    
    def end_headers(self):
        # Security headers for remote access
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Content-Security-Policy', "default-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data:;")
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Log all access attempts with security warnings
        client_ip = self.client_address[0]
        if client_ip not in ['127.0.0.1', 'localhost', '::1']:
            print(f"⚠️  REMOTE ACCESS: {client_ip}:{self.client_address[1]} - {format % args}")
        else:
            print(f"✅ LOCAL ACCESS: {client_ip}:{self.client_address[1]} - {format % args}")
    
    def do_GET(self):
        # Allow all access but log remote attempts
        super().do_GET()

def get_local_ip():
    """Get the local IP address for remote access."""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "0.0.0.0"

def start_remote_access_server(port=8000, bind_host=None):
    """Start an HTTP server with remote access capabilities."""
    
    if bind_host is None:
        bind_host = get_local_ip()
    
    print("⚠️  REMOTE ACCESS SERVER STARTUP - EXO-SUIT V5.0")
    print("=" * 50)
    print("🚨 SECURITY WARNING: This server allows external access!")
    print("   Only use in trusted, controlled environments")
    print("   Consider using local-security-config.py for development")
    print()
    
    # Security confirmation
    if bind_host != "127.0.0.1":
        print(f"🔓 REMOTE ACCESS ENABLED")
        print(f"   Host: {bind_host}")
        print(f"   Port: {port}")
        print(f"   URL: http://{bind_host}:{port}")
        print(f"   External access: ALLOWED")
        print()
        
        confirm = input("⚠️  Are you sure you want to enable remote access? (yes/no): ")
        if confirm.lower() != "yes":
            print("🚫 Remote access cancelled")
            sys.exit(0)
    else:
        print(f"🔒 LOCAL ACCESS ONLY")
        print(f"   Host: {bind_host}")
        print(f"   Port: {port}")
        print(f"   URL: http://{bind_host}:{port}")
        print(f"   External access: BLOCKED")
        print()
    
    # Create server
    with socketserver.TCPServer((bind_host, port), RemoteAccessServer) as httpd:
        print(f"🚀 Server started successfully!")
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
    
    parser = argparse.ArgumentParser(
        description="Start remote access server for Exo-Suit V5.0 (⚠️ USE WITH CAUTION)",
        epilog="⚠️  WARNING: Remote access can expose your system to external threats!"
    )
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--host", type=str, help="Host to bind (default: auto-detect local IP)")
    parser.add_argument("--local", action="store_true", help="Force localhost binding only")
    
    args = parser.parse_args()
    
    if args.local:
        bind_host = "127.0.0.1"
    else:
        bind_host = args.host
    
    start_remote_access_server(args.port, bind_host)
