#!/usr/bin/env python3
"""
Simple HTTP Server for Sandoog Integration Tool

This script provides a local development server with CORS headers
to run the Sandoog Integration Tool in a web browser.
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers"""
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key, X-API-Signature, X-API-Timestamp')
        self.send_header('Access-Control-Max-Age', '86400')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight OPTIONS requests"""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging to show requests"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    """Main function to start the server"""
    port = 8080
    
    # Check if port is already in use
    try:
        with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
            print("=" * 60)
            print("🚀 Sandoog Integration Tool - Development Server")
            print("=" * 60)
            print(f"📁 Serving files from: {os.getcwd()}")
            print(f"🌐 Server running at: http://localhost:{port}")
            print(f"📱 Open your browser and navigate to: http://localhost:{port}")
            print("=" * 60)
            print("📋 Features:")
            print("   ✅ CORS headers enabled for API requests")
            print("   ✅ Automatic file serving")
            print("   ✅ Request logging")
            print("=" * 60)
            print("🛑 Press Ctrl+C to stop the server")
            print("=" * 60)
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 Server stopped by user")
                httpd.shutdown()
                
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {port} is already in use.")
            print(f"💡 Try using a different port: python server.py {port + 1}")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 