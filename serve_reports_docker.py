#!/usr/bin/env python3
"""
Simple HTTP Server for serving event detail reports (Docker version)
รัน server เพื่อให้ Mattermost เข้าถึงไฟล์ HTML reports ได้
"""

import http.server
import socketserver
import os
import sys

# Configuration - use /app for Docker
PORT = int(os.getenv('REPORT_SERVER_PORT', '8080'))
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), '')

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def _is_blocked(self, path):
        """ตรวจสอบว่า path ถูกบล็อกหรือไม่"""
        name = os.path.basename(path.rstrip('/'))
        if not name:
            return False
        if name.startswith('.'):
            return True
        if name in ('logs', 'data', 'backups'):
            return True
        if name.endswith('.py') or name.endswith('.db') or name.endswith('.log'):
            return True
        return False
    
    def list_directory(self, path):
        """ปิด directory listing - ห้ามแสดงรายการไฟล์"""
        self.send_error(403, "Directory listing is disabled")
        return None
    
    def do_GET(self):
        """Override เพื่อบล็อกไฟล์ที่ละเอียดอ่อน"""
        # หา path จริง (แปลง URL path เป็นไฟล์ path)
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')
        if self._is_blocked(path):
            self.send_error(403, "Forbidden")
            return
        super().do_GET()
    
    def end_headers(self):
        # เพิ่ม CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Override to add timestamp"""
        sys.stdout.write("%s - [%s] %s\n" %
                        (self.address_string(),
                         self.log_date_time_string(),
                         format%args))

def get_local_ip():
    """Get local IP address"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "unknown"

def main():
    """Start HTTP server"""
    os.chdir(DIRECTORY)
    
    # Bind to 0.0.0.0 เพื่อให้เข้าถึงได้จากเครื่องอื่น
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        local_ip = get_local_ip()
        container_name = os.getenv('HOSTNAME', 'container')
        
        print("=" * 70)
        print(f"  🌐 HTTP Report Server Started")
        print("=" * 70)
        print(f"\n  📂 Serving directory: {DIRECTORY}")
        print(f"  🐳 Container: {container_name}")
        print(f"  🔗 Local URL: http://localhost:{PORT}")
        print(f"  🔗 Network URL: http://{local_ip}:{PORT}")
        print(f"  🔗 Docker URL: http://report-server:{PORT}")
        print(f"\n  📄 Access reports at:")
        print(f"     http://{local_ip}:{PORT}/event_detail/event_details_YYYY-MM-DD.html")
        print(f"\n  Press Ctrl+C to stop")
        print("\n" + "=" * 70)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n⚠️  Server stopped by user")
            httpd.shutdown()

if __name__ == "__main__":
    main()
