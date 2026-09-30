from http.server import BaseHTTPRequestHandler
import json
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # التوكن محفور جوا الكود زي ما طلبت يا برنس
            token = "8960593021:AAFkF-8Cvt_jsOHJmNUyBGWMvzmE0hIbMbk"
            
            if 'message' in data:
                chat_id = data['message']['chat']['id']
                text = data['message'].get('text', '')
                
                # الرد التجريبي للتأكيد
                reply_text = f"يا هلا يا شريك! وصلتني رسالتك: {text}"
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
        
