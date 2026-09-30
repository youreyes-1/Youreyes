from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import sqlite3
import os
import random
import time

TOKEN = "8960593021:AAFkF-8Cvt_jsOHJmNUyBGWMvzmE0hIbMbk"
OWNER_ID = 6610111288
DB_PATH = "/tmp/doge_bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        balance REAL DEFAULT 0.0,
                        mining_speed REAL DEFAULT 0.001,
                        last_mine INTEGER DEFAULT 0,
                        verified INTEGER DEFAULT 0,
                        ref_count INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        link TEXT,
                        name TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT,
                        reward REAL DEFAULT 0.0002)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT)''')
    conn.commit()
    conn.close()

init_db()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            if 'message' in data:
                msg = data['message']
                chat_id = msg['chat']['id']
                user_id = msg['from']['id']
                text = msg.get('text', '')
                self.handle_message(chat_id, user_id, text)
                
            elif 'callback_query' in data:
                cq = data['callback_query']
                chat_id = cq['message']['chat']['id']
                user_id = cq['from']['id']
                data_val = cq['data']
                message_id = cq['message']['message_id']
                self.handle_callback(chat_id, user_id, data_val, message_id)
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
        return

    def handle_message(self, chat_id, user_id, text):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT verified FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()
            row = (0,)
            
        is_verified = row[0]
        conn.close()

        if text == "/start":
            if not is_verified:
                self.send_captcha(chat_id)
            else:
                self.send_main_menu(chat_id, user_id)
        elif user_id == OWNER_ID and text == "/owner":
            self.send_owner_panel(chat_id)
        else:
            if is_verified:
                self.send_main_menu(chat_id, user_id)
            else:
                self.send_captcha(chat_id)

    def handle_callback(self, chat_id, user_id, data, message_id):
        if data.startswith("captcha_"):
            ans = data.split("_")[1]
            if ans == "correct":
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET verified = 1 WHERE user_id = ?", (user_id,))
                conn.commit()
                conn.close()
                self.send_message(chat_id, "✅ يا برنس! تجاوزت الكابتشا بنجاح ودخلت مملكة الدوج كوين.")
                self.send_main_menu(chat_id, user_id)
            else:
                self.send_message(chat_id, "❌ إجابة خاطئة يا زول، حاول تاني وركز!")
                self.send_captcha(chat_id)
                
        elif data == "menu_mine":
            self.do_mining(chat_id, user_id)
        elif data == "menu_tasks":
            self.show_tasks(chat_id)
        elif data == "menu_channels":
            self.show_channels(chat_id)
        elif data == "menu_info":
            self.show_info(chat_id)
        elif data == "menu_withdraw":
            self.show_withdraw(chat_id)
        elif data == "owner_panel" and user_id == OWNER_ID:
            self.send_owner_panel(chat_id)
        elif data == "owner_add_ch" and user_id == OWNER_ID:
            self.send_message(chat_id, "📢 لإضافة قناة، استخدم الأمر:\n`/addchan [الرابط] [اسم القناة]`")
        elif data == "owner_add_task" and user_id == OWNER_ID:
            self.send_message(chat_id, "📋 لإضافة مهمة، استخدم الأمر:\n`/addtask [الوصف]`")

    def send_captcha(self, chat_id):
        keyboard = {
            "inline_keyboard": [
                [
                    {"text": "🍎 تفاحة", "callback_data": "captcha_wrong"},
                    {"text": "🚗 سيارة (اضغط هنا)", "callback_data": "captcha_correct"},
                    {"text": "⚽ كورة", "callback_data": "captcha_wrong"}
                ]
            ]
        }
        text = "🤖 **تحقق أمني (حماية ضد البوتات):**\n\nاختر زر **سيارة** لتثبت أنك انسان مش بوت وتربح أول مكسب!"
        self.send_message_with_keyboard(chat_id, text, keyboard)

    def send_main_menu(self, chat_id, user_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT balance, mining_speed FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        balance = row[0] if row else 0.0
        speed = row[1] if row else 0.001

        keyboard_buttons = [
            [{"text": "⛏️ حصاد التعدين اليومي", "callback_data": "menu_mine"}],
            [{"text": "📋 المهام المربحة (0.0002)", "callback_data": "menu_tasks"}, {"text": "📢 قنوات زيادة السرعة (+10%)", "callback_data": "menu_channels"}],
            [{"text": "💰 سحب الأرباح", "callback_data": "menu_withdraw"}, {"text": "ℹ️ معلومات مهمة", "callback_data": "menu_info"}]
        ]
        
        if user_id == OWNER_ID:
            keyboard_buttons.append([{"text": "👑 لوحة تحكم المالك المطلقة", "callback_data": "owner_panel"}])

        keyboard = {"inline_keyboard": keyboard_buttons}
        text = f"🌟 **صنبور دوج كوين العملاق**\n\n👤 رصيدك الحالي: `{balance:.6f}` DOGE\n⚡ سرعة التعدين: `{speed:.4f}` DOGE/يوم\n\nاختر ما تحب من القائمة أدناه:"
        self.send_message_with_keyboard(chat_id, text, keyboard)

    def do_mining(self, chat_id, user_id):
        current_time = int(time.time())
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT balance, mining_speed, last_mine FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return
            
        balance, speed, last_mine = row
        if current_time - last_mine < 86400:
            remaining = 86400 - (current_time - last_mine)
            hours = remaining // 3600
            self.send_message(chat_id, f"⏳ يا زول اصبر شوية! التعدين بيفتح بعد `{hours}` ساعة.")
            conn.close()
            return

        added_amount = speed
        new_balance = balance + added_amount
        cursor.execute("UPDATE users SET balance = ?, last_mine = ? WHERE user_id = ?", (new_balance, current_time, user_id))
        conn.commit()
        conn.close()
        
        self.send_message(chat_id, f"🎉 مبروك! أضفت `{added_amount:.6f}` DOGE إلى محفظتك بنجاح.")
        self.send_main_menu(chat_id, user_id)

    def show_tasks(self, chat_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, description, reward FROM tasks")
        tasks = cursor.fetchall()
        conn.close()
        
        if not tasks:
            text = "📋 لا توجد مهام حالياً، انتظر المالك لينزل مهام جديدة!"
        else:
            text = "📋 **المهام المتاحة:**\n\n"
            for t in tasks:
                text += f"- {t[1]} (المكافأة: `{t[2]}` DOGE)\n"
        self.send_message(chat_id, text)

    def show_channels(self, chat_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT link, name FROM channels")
        channels = cursor.fetchall()
        conn.close()
        
        text = "📢 **قنوات زيادة سرعة التعدين (+10% لكل قناة):**\n\n"
        if not channels:
            text += "لا توجد قنوات مضافة حالياً."
        else:
            for ch in channels:
                text += f"🔗 [{ch[1]}]({ch[0]})\n"
        self.send_message(chat_id, text)

    def show_info(self, chat_id):
        text = "ℹ️ **معلومات مهمة للبوت:**\n\n1️⃣ الصنبور يدفع عملة Dogecoin حقيقية.\n2️⃣ كل اشتراك في قناة يزود سرعتك بنسبة 10%.\n3️⃣ السحب الأول يبدأ من 0.01 دوج لزيادة الثقة، وبعدها يتطلب إحالات لتفادي الضغط.\n4️⃣ المالك يتحكم بكل الإعدادات."
        self.send_message(chat_id, text)

    def show_withdraw(self, chat_id):
        text = "💰 **سحب الأرباح:**\n\nالحد الأدنى للسحب الأول هو `0.01` DOGE.\n⚠️ تذكير: السحب الثاني يتطلب جلب إحالات (2 ثم 10 إحالات) لضمان استمرار الشبكة."
        self.send_message(chat_id, text)

    def send_owner_panel(self, chat_id):
        keyboard = {
            "inline_keyboard": [
                [{"text": "➕ إضافة قناة جديدة", "callback_data": "owner_add_ch"}],
                [{"text": "➕ إضافة مهمة جديدة", "callback_data": "owner_add_task"}],
                [{"text": "🔙 العودة للقائمة الرئيسية", "callback_data": "menu_mine"}]
            ]
        }
        text = "👑 **لوحة تحكم المالك المطلقة:**\n\nأنت تملك صلاحيات كاملة لتعديل كل مفاصل البوت."
        self.send_message_with_keyboard(chat_id, text, keyboard)

    def send_message(self, chat_id, text):
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}).encode('utf-8')
        req = urllib.request.Request(api_url, data=payload, headers={'Content-Type': 'application/json'})
        try:
            urllib.request.urlopen(req)
        except Exception:
            pass

    def send_message_with_keyboard(self, chat_id, text, keyboard):
        api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": chat_id, "text": text, "reply_markup": keyboard, "parse_mode": "Markdown"}).encode('utf-8')
        req = urllib.request.Request(api_url, data=payload, headers={'Content-Type': 'application/json'})
        try:
            urllib.request.urlopen(req)
        except Exception:
            pass
        
