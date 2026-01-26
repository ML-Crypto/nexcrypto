"""
NEX Website 簡易伺服器
- 提供靜態網頁服務
- 提供文章 API（讀取/儲存）
"""

import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 8080
DATA_FILE = 'data/news.json'

class WebsiteHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)

        # API: 取得文章
        if parsed.path == '/api/news':
            self.send_json_response(self.load_news())
        else:
            # 靜態檔案
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        # API: 儲存文章
        if parsed.path == '/api/news':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))
                self.save_news(data)
                self.send_json_response({'success': True, 'message': '儲存成功'})
            except Exception as e:
                self.send_json_response({'success': False, 'message': str(e)}, 500)
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        # 處理 CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))

    def load_news(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'articles': [], 'lastUpdated': None}

    def save_news(self, data):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def log_message(self, format, *args):
        # 簡化日誌輸出
        if '/api/' in args[0] or args[0].endswith('.html'):
            print(f"[{self.log_date_time_string()}] {args[0]}")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    server = HTTPServer(('0.0.0.0', PORT), WebsiteHandler)
    print(f"""
╔══════════════════════════════════════════╗
║       NEX Website Server 已啟動          ║
╠══════════════════════════════════════════╣
║  網站首頁: http://localhost:{PORT}          ║
║  後台管理: http://localhost:{PORT}/admin.html ║
╚══════════════════════════════════════════╝
    """)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n伺服器已停止")
        server.shutdown()


if __name__ == '__main__':
    main()
