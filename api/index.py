from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import sqlite3
import time
import random
import re

TOKEN = "8960593021:AAFkF-8Cvt_jsOHJmNUyBGWMvzmE0hIbMbk"
OWNER_ID = 6610111288
BOT_USERNAME = "Dogcoinibot"
DB_PATH = "/tmp/doge_bot.db"
MIN_WITHDRAW = 0.01

# ================= قاعدة البيانات =================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY, phone TEXT, balance REAL DEFAULT 0.0,
                    speed REAL DEFAULT 0.0000000115, last_update INTEGER,
                    captcha_time INTEGER DEFAULT 0, referrer_id INTEGER DEFAULT 0, state TEXT DEFAULT 'idle')''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, ch_id TEXT, type TEXT)''') # type: 'main' or 'speed'
    c.execute('''CREATE TABLE IF NOT EXISTS shortlinks (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, password TEXT, reward REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS custom_btns (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT)''')
    c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (OWNER_ID,))
    conn.commit()
    conn.close()

init_db()

# ================= دوال التيليجرام =================
def call_api(method, payload):
    api_url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    req = urllib.request.Request(api_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try: return json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    except: return None

def send_msg(chat_id, text, markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if markup: payload["reply_markup"] = markup
    call_api("sendMessage", payload)

def edit_msg(chat_id, msg_id, text, markup=None):
    payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML"}
    if markup: payload["reply_markup"] = markup
    call_api("editMessageText", payload)

def check_sub(user_id, channel_id):
    res = call_api("getChatMember", {"chat_id": channel_id, "user_id": user_id})
    if res and res.get('ok'):
        status = res['result']['status']
        return status in ['member', 'administrator', 'creator']
    return False

# ================= المحرك الأساسي =================
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            if 'message' in data: self.handle_message(data['message'])
            elif 'callback_query' in data: self.handle_callback(data['callback_query'])
            self.send_response(200)
            self.end_headers()
        except:
            self.send_response(500)
            self.end_headers()
        return

    def handle_message(self, msg):
        chat_id = msg['chat']['id']
        user_id = msg['from']['id']
        text = msg.get('text', '')
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
        is_admin = c.fetchone() is not None

        c.execute("SELECT phone, captcha_time, state, balance FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        now = int(time.time())
        
        if not user:
            ref_id = 0
            if text.startswith("/start ") and text.split(" ")[1].isdigit():
                ref_id = int(text.split(" ")[1])
                # مكافأة الإحالة المباشرة للمحيل
                c.execute("UPDATE users SET speed = speed * 1.3 WHERE user_id = ?", (ref_id,))
            c.execute("INSERT INTO users (user_id, last_update, referrer_id) VALUES (?, ?, ?)", (user_id, now, ref_id))
            conn.commit()
            user = (None, 0, 'idle', 0.0)

        phone, captcha_time, state, balance = user

        # 1. التحقق من الرقم (حظر الغرب)
        if not phone:
            if 'contact' in msg and msg['contact']['user_id'] == user_id:
                p = msg['contact']['phone_number']
                if not p.startswith('+'): p = '+' + p
                if re.match(r'^\+(1|3|4|61)', p) and not p.startswith('+7'):
                    send_msg(chat_id, "❌ الأرقام من هذه الدولة غير مدعومة.")
                    return
                c.execute("UPDATE users SET phone = ? WHERE user_id = ?", (p, user_id))
                conn.commit()
                self.send_captcha(chat_id)
            else:
                markup = {"keyboard": [[{"text": "📱 تحقق من رقم الهاتف", "request_contact": True}]], "resize_keyboard": True}
                send_msg(chat_id, "🔒 <b>حماية النظام:</b> أرسل رقم هاتفك لفتح حسابك.", markup)
            return

        # 2. الكابتشا
        if now - captcha_time > 3600:
            self.send_captcha(chat_id)
            return

        # 3. إجبار الاشتراك بالقناة الرئيسية
        c.execute("SELECT url, ch_id FROM channels WHERE type = 'main'")
        main_channels = c.fetchall()
        for ch_url, ch_id in main_channels:
            if not check_sub(user_id, ch_id):
                markup = {"inline_keyboard": [[{"text": "📢 اشترك الآن", "url": ch_url}], [{"text": "✅ تحقق من الاشتراك", "callback_data": "check_main_sub"}]]}
                send_msg(chat_id, "⚠️ <b>عفواً!</b>\nيجب الاشتراك في قناة البوت الرسمية أولاً لتتمكن من السحب والتعدين.", markup)
                return

        # 4. معالجة حالات الإدخال (State Machine)
        if state == 'wait_wallet':
            # إرسال إشعار للمالك والمشرفين
            c.execute("SELECT user_id FROM admins")
            for admin in c.fetchall():
                send_msg(admin[0], f"🔔 <b>طلب سحب جديد!</b>\n\n👤 المستخدم: <code>{user_id}</code>\n💰 الرصيد: <code>{balance:.5f}</code> DOGE\n🏦 المحفظة:\n<code>{text}</code>")
            
            # تصفير الرصيد وإرجاع الحالة
            c.execute("UPDATE users SET balance = 0, state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "✅ <b>تم استلام طلب السحب بنجاح!</b>\nستصلك العملات على محفظتك قريباً بعد المراجعة.")
            self.send_main_menu(chat_id, user_id, c)
            return

        elif state.startswith('wait_pass_'):
            link_id = int(state.split('_')[2])
            c.execute("SELECT password, reward FROM shortlinks WHERE id = ?", (link_id,))
            link = c.fetchone()
            if link and text.strip() == link[0]:
                c.execute("UPDATE users SET balance = balance + ?, state = 'idle' WHERE user_id = ?", (link[1], user_id))
                conn.commit()
                send_msg(chat_id, f"🎉 <b>رائع!</b> تمت إضافة {link[1]} DOGE لرصيدك.")
            else:
                c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
                conn.commit()
                send_msg(chat_id, "❌ <b>كلمة السر خاطئة!</b>")
            self.send_main_menu(chat_id, user_id, c)
            return

        elif state == 'admin_wait_broadcast' and is_admin:
            c.execute("SELECT user_id FROM users")
            for u in c.fetchall(): send_msg(u[0], f"📢 <b>إعلان هام:</b>\n\n{text}")
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "✅ تم إرسال الإذاعة بنجاح.")
            return

        elif state == 'admin_wait_admin_id' and user_id == OWNER_ID:
            c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (int(text),))
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "✅ تم رفع المستخدم كمشرف بنجاح.")
            return

        # 5. الأوامر العادية
        if text == "/start":
            self.send_main_menu(chat_id, user_id, c)
        elif text == "/admin" and is_admin:
            self.send_admin_panel(chat_id, user_id)

        conn.close()

    def handle_callback(self, cq):
        chat_id = cq['message']['chat']['id']
        user_id = cq['from']['id']
        data = cq['data']
        msg_id = cq['message']['message_id']
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
        is_admin = c.fetchone() is not None

        if data == "cap_ok":
            c.execute("UPDATE users SET captcha_time = ? WHERE user_id = ?", (int(time.time()), user_id))
            conn.commit()
            edit_msg(chat_id, msg_id, "✅ تم التحقق البشري.")
            self.send_main_menu(chat_id, user_id, c)
        elif data == "cap_fail":
            edit_msg(chat_id, msg_id, "❌ فشل التحقق، حاول مجدداً.")
            self.send_captcha(chat_id)
            
        elif data == "check_main_sub":
            edit_msg(chat_id, msg_id, "🔄 جاري التحقق من الاشتراك...")
            # عند إرسال رسالة جديدة، سيمر عبر handle_message للتحقق مرة أخرى
            self.send_main_menu(chat_id, user_id, c)

        elif data == "refresh_mine":
            self.update_mining(user_id, c)
            conn.commit()
            self.edit_main_menu(chat_id, user_id, msg_id, c)
            
        elif data == "req_withdraw":
            self.update_mining(user_id, c)
            c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            bal = c.fetchone()[0]
            if bal < MIN_WITHDRAW:
                call_api("answerCallbackQuery", {"callback_query_id": cq['id'], "text": f"❌ رصيدك أقل من الحد الأدنى ({MIN_WITHDRAW} DOGE).", "show_alert": True})
            else:
                c.execute("UPDATE users SET state = 'wait_wallet' WHERE user_id = ?", (user_id,))
                conn.commit()
                send_msg(chat_id, "💸 <b>السحب المباشر:</b>\n\nأرسل الآن عنوان محفظة <b>Dogecoin (FaucetPay)</b> الخاصة بك لطلب السحب:")

        elif data == "show_team":
            link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
            text = f"👥 <b>نظام الإحالات الخاص بك:</b>\n\nكل شخص تدعوه يمنحك زيادة +30% في سرعة التعدين.\n\n🔗 رابط الدعوة الخاص بك:\n<code>{link}</code>"
            send_msg(chat_id, text)

        elif data == "show_tasks":
            c.execute("SELECT id, reward FROM shortlinks")
            links = c.fetchall()
            btns = [[{"text": f"🔗 مهمة تخطي (+{l[1]} DOGE)", "callback_data": f"do_link_{l[0]}"}] for l in links]
            send_msg(chat_id, "📋 <b>المهام المربحة المتوفرة:</b>", {"inline_keyboard": btns} if btns else None)

        elif data.startswith("do_link_"):
            link_id = data.split("_")[2]
            c.execute("UPDATE users SET state = ? WHERE user_id = ?", (f"wait_pass_{link_id}", user_id))
            conn.commit()
            send_msg(chat_id, "🔗 <b>تخطي الرابط:</b>\n1. ادخل الرابط وتخطى الإعلانات.\n2. انسخ كلمة السر من الصفحة الأخيرة.\n3. أرسل كلمة السر هنا الآن:")

        # ================= أزرار لوحة المشرفين =================
        elif data == "admin_panel" and is_admin:
            self.send_admin_panel(chat_id, user_id)
            
        elif data == "admin_broadcast" and is_admin:
            c.execute("UPDATE users SET state = 'admin_wait_broadcast' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "📢 أرسل نص الإذاعة الآن:")
            
        elif data == "admin_add_admin" and user_id == OWNER_ID:
            c.execute("UPDATE users SET state = 'admin_wait_admin_id' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "👑 أرسل <b>الآيدي (ID)</b> الخاص بالمشرف الجديد:")

        conn.close()

    # ================= الدوال المساعدة =================
    def send_captcha(self, chat_id):
        btns = [{"text": "🔹", "callback_data": "cap_fail"} for _ in range(3)]
        btns.insert(random.randint(0, 3), {"text": "🔴", "callback_data": "cap_ok"})
        send_msg(chat_id, "🤖 <b>نظام الحماية:</b>\nاضغط على الرمز المختلف (🔴) للبدء.", {"inline_keyboard": [btns]})

    def update_mining(self, user_id, cursor):
        now = int(time.time())
        cursor.execute("SELECT balance, speed, last_update FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            bal, speed, last = row
            earned = (now - last) * speed
            cursor.execute("UPDATE users SET balance = ?, last_update = ? WHERE user_id = ?", (bal + earned, now, user_id))

    def get_main_menu(self, user_id, cursor):
        btns = [
            [{"text": "🔄 تحديث الأرباح", "callback_data": "refresh_mine"}],
            [{"text": "💸 سحب الرصيد", "callback_data": "req_withdraw"}, {"text": "👥 فريقك للإحالات", "callback_data": "show_team"}],
            [{"text": "🔗 المهام والروابط", "callback_data": "show_tasks"}, {"text": "📢 قنوات السرعة (+10%)", "callback_data": "show_speed_ch"}]
        ]
        cursor.execute("SELECT name, url FROM custom_btns")
        for btn in cursor.fetchall(): btns.append([{"text": btn[0], "url": btn[1]}])
        cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
        if cursor.fetchone(): btns.append([{"text": "⚙️ لوحة التحكم المطلقة", "callback_data": "admin_panel"}])
        return {"inline_keyboard": btns}

    def send_main_menu(self, chat_id, user_id, cursor):
        self.update_mining(user_id, cursor)
        cursor.execute("SELECT balance, speed FROM users WHERE user_id = ?", (user_id,))
        bal, speed = cursor.fetchone()
        text = f"⛏️ <b>مركز تعدين Dogecoin</b>\n\n💰 رصيدك: <code>{bal:.6f}</code> <b>DOGE</b>\n⚡ السرعة: <code>{speed*86400:.4f}</code> DOGE/يوم\n\n<i>اضغط تحديث الأرباح لجمع تعدينك المباشر.</i>"
        send_msg(chat_id, text, self.get_main_menu(user_id, cursor))

    def edit_main_menu(self, chat_id, user_id, msg_id, cursor):
        cursor.execute("SELECT balance, speed FROM users WHERE user_id = ?", (user_id,))
        bal, speed = cursor.fetchone()
        text = f"⛏️ <b>مركز تعدين Dogecoin</b>\n\n💰 رصيدك: <code>{bal:.6f}</code> <b>DOGE</b>\n⚡ السرعة: <code>{speed*86400:.4f}</code> DOGE/يوم\n\n<i>اضغط تحديث الأرباح لجمع تعدينك المباشر.</i>"
        edit_msg(chat_id, msg_id, text, self.get_main_menu(user_id, cursor))

    def send_admin_panel(self, chat_id, user_id):
        btns = [
            [{"text": "📢 إذاعة للجميع", "callback_data": "admin_broadcast"}],
            [{"text": "➕ إضافة قناة إجبارية", "callback_data": "add_main_ch"}, {"text": "➕ إضافة قناة سرعة", "callback_data": "add_speed_ch"}],
            [{"text": "🔗 إضافة رابط وكلمة سر", "callback_data": "add_shortlink"}, {"text": "🔘 إضافة زر مخصص", "callback_data": "add_custom_btn"}]
        ]
        if user_id == OWNER_ID: btns.append([{"text": "👑 إضافة مشرف فرعي", "callback_data": "admin_add_admin"}])
        send_msg(chat_id, "⚙️ <b>لوحة التحكم والإدارة:</b>", {"inline_keyboard": btns})
                                                   
