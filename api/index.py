from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # سحب التوكن من متغيرات البيئة في فيرسيل
            token = os.environ.get('TELEGRAM_BOT_TOKEN')
            
            if 'message' in data:
                chat_id = data['message']['chat']['id']
                text = data['message'].get('text', '')
                
                # الرد التجريبي أو استقبال الترافيك
                reply_text = f"يا هلا يا شريك! وصلتنـي رسالتك: {text}"
                send_telegram_message(token, chat_id, reply_text)
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            
        return

def send_telegram_message(token, chat_id, text):
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode('utf-8')
    req = urllib.request.Request(api_url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        urllib.request.urlopen(req)
    except Exception:
        pass
      
