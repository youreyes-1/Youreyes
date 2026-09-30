from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import sqlite3
import time
import random
import re
import traceback

# ================= الإعدادات الأساسية =================
TOKEN = "8960593021:AAFkF-8Cvt_jsOHJmNUyBGWMvzmE0hIbMbk"
OWNER_ID = 6610111288
BOT_USERNAME = "Dogcoinibot"
DB_PATH = "/tmp/doge_bot_v4.db" # تم التغيير لضمان مسح أي كاش قديم
MIN_WITHDRAW = 0.01

# ================= قاموس اللغات والأزرار السفلية =================
LANG = {
    'ar': {
        'btn_refresh': "🔄 تحديث الأرباح",
        'btn_withdraw': "💸 سحب الرصيد",
        'btn_team': "👥 فريقك",
        'btn_tasks': "🔗 المهام المربحة",
        'btn_lang': "🌐 English",
        'phone_btn': "📱 مشاركة جهة الاتصال (إجباري)",
        'captcha_msg': "🤖 <b>نظام الحماية ضد الروبوتات:</b>\n\nاضغط على الرمز المختلف (🔴) للبدء في جمع Dogecoin.",
        'phone_req': "🔒 <b>خطوة أمنية أخيرة:</b>\n\nلضمان عدم استخدام حسابات وهمية، يرجى مشاركة رقم هاتفك عبر الزر أدناه.",
        'phone_err': "❌ عذراً، الأرقام من هذه الدولة محظورة في نظامنا.",
        'sub_req': "⚠️ <b>تنبيه هام!</b>\n\nيجب عليك الاشتراك في قنواتنا الرسمية أولاً.",
        'main_menu': "⛏️️ <b>بيانات التعدين المباشرة</b>\n\n💰 رصيدك: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ السرعة: <code>{speed:.8f}</code> DOGE/يوم\n👥 الفريق: <code>{refs}</code>\n\n<i>تم تحديث بياناتك بنجاح!</i>",
        'team_msg': "👥 <b>نظام الإحالات (زيادة 30%):</b>\n\nالأعضاء النشطين: <code>{refs}</code>\n\n🔗 رابطك:\n<code>{link}</code>",
        'withdraw_err': "❌ رصيدك أقل من الحد الأدنى ({min} DOGE).",
        'withdraw_req': "💸 <b>سحب الأرباح:</b>\nأرسل الآن عنوان محفظة <b>Dogecoin (FaucetPay)</b>:",
        'withdraw_done': "✅ <b>تم استلام طلبك!</b>\nالرصيد قيد المراجعة.",
        'task_msg': "🔗 <b>المهام المتوفرة:</b>\nاضغط على المهمة، تخطى الإعلانات، ثم أرسل كلمة السر هنا:",
        'task_ok': "🎉 <b>إجابة صحيحة!</b> تمت إضافة {reward:.8f} DOGE لرصيدك.",
        'task_err': "❌ <b>كلمة السر خاطئة!</b> حاول مرة أخرى.",
        'admin_panel': "👑 <b>لوحة الإدارة المطلقة:</b>",
    },
    'en': {
        'btn_refresh': "🔄 Refresh Balance",
        'btn_withdraw': "💸 Withdraw",
        'btn_team': "👥 Your Team",
        'btn_tasks': "🔗 Profitable Tasks",
        'btn_lang': "🌐 العربية",
        'phone_btn': "📱 Share Contact (Required)",
        'captcha_msg': "🤖 <b>Anti-Bot Security:</b>\n\nClick the different symbol (🔴) to start.",
        'phone_req': "🔒 <b>Final Step:</b>\n\nPlease share your phone number using the button below.",
        'phone_err': "❌ Numbers from this region are blocked.",
        'sub_req': "⚠️ <b>Important!</b>\n\nYou must subscribe to our official channels first.",
        'main_menu': "⛏️ <b>Live Mining Data</b>\n\n💰 Balance: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ Speed: <code>{speed:.8f}</code> DOGE/Day\n👥 Team: <code>{refs}</code>\n\n<i>Data updated successfully!</i>",
        'team_msg': "👥 <b>Referral System (+30%):</b>\n\nActive Members: <code>{refs}</code>\n\n🔗 Your Link:\n<code>{link}</code>",
        'withdraw_err': "❌ Balance is below minimum ({min} DOGE).",
        'withdraw_req': "💸 <b>Withdraw Funds:</b>\nSend your <b>Dogecoin (FaucetPay)</b> wallet address:",
        'withdraw_done': "✅ <b>Request Received!</b>\nUnder review.",
        'task_msg': "🔗 <b>Available Tasks:</b>\nClick, skip ads, and send the password here:",
        'task_ok': "🎉 <b>Correct!</b> {reward:.8f} DOGE added.",
        'task_err': "❌ <b>Wrong Password!</b> Try again.",
        'admin_panel': "👑 <b>Absolute Admin Panel:</b>",
    }
}

# ================= قاعدة البيانات =================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY, phone TEXT, balance REAL DEFAULT 0.0,
                    speed REAL DEFAULT 0.0000000115, last_update INTEGER,
                    captcha_time INTEGER DEFAULT 0, referrer_id INTEGER DEFAULT 0,
                    ref_count INTEGER DEFAULT 0, state TEXT DEFAULT 'idle', lang TEXT DEFAULT 'ar')''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)''')
    c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (OWNER_ID,))
    c.execute('''CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, ch_id TEXT, type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS shortlinks (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, password TEXT, reward REAL)''')
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

def check_sub(user_id, channel_id):
    res = call_api("getChatMember", {"chat_id": channel_id, "user_id": user_id})
    if res and res.get('ok'):
        return res['result']['status'] in ['member', 'administrator', 'creator']
    return False

# ================= المحرك الأساسي =================
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            if not body:
                self.send_response(200)
                self.end_headers()
                return
                
            data = json.loads(body.decode('utf-8'))
            
            if 'message' in data: 
                try: self.handle_message(data['message'])
                except Exception: send_msg(OWNER_ID, f"⚠️ <b>Crash MSG:</b>\n<code>{traceback.format_exc()[-800:]}</code>")
            elif 'callback_query' in data: 
                try: self.handle_callback(data['callback_query'])
                except Exception: send_msg(OWNER_ID, f"⚠️ <b>Crash BTN:</b>\n<code>{traceback.format_exc()[-800:]}</code>")
                
        except Exception: pass
            
        self.send_response(200)
        self.end_headers()
        return

    def get_text(self, lang, key, **kwargs):
        text = LANG.get(lang, LANG['ar']).get(key, "")
        if kwargs: text = text.format(**kwargs)
        return text

    # بناء الكيبورد السفلي
    def get_reply_keyboard(self, lang):
        kb = [
            [{"text": self.get_text(lang, 'btn_refresh')}],
            [{"text": self.get_text(lang, 'btn_withdraw')}, {"text": self.get_text(lang, 'btn_team')}],
            [{"text": self.get_text(lang, 'btn_tasks')}, {"text": self.get_text(lang, 'btn_lang')}]
        ]
        return {"keyboard": kb, "resize_keyboard": True}

    def handle_message(self, msg):
        chat_id = msg['chat']['id']
        user_id = msg['from']['id']
        text = msg.get('text', '')
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
        is_admin = c.fetchone() is not None

        c.execute("SELECT phone, captcha_time, state, balance, lang, referrer_id FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        now = int(time.time())
        
        if not user:
            ref_id = 0
            if text.startswith("/start ") and text.split(" ")[1].isdigit():
                ref_id = int(text.split(" ")[1])
            c.execute("INSERT INTO users (user_id, last_update, referrer_id) VALUES (?, ?, ?)", (user_id, now, ref_id))
            conn.commit()
            user = (None, 0, 'idle', 0.0, 'ar', ref_id)

        phone, captcha_time, state, balance, lang, ref_id = user
        bal_float = float(balance or 0)

        # 1. التحقق من الرقم 
        if not phone:
            if 'contact' in msg:
                p = msg['contact'].get('phone_number', '')
                if not p.startswith('+'): p = '+' + p
                if re.match(r'^\+(1|3|4|61)', p) and not p.startswith('+7'):
                    send_msg(chat_id, self.get_text(lang, 'phone_err'), {"remove_keyboard": True})
                    return
                c.execute("UPDATE users SET phone = ? WHERE user_id = ?", (p, user_id))
                conn.commit()
                send_msg(chat_id, "✅", {"remove_keyboard": True}) # إزالة كيبورد الرقم
                self.send_captcha(chat_id, lang)
            else:
                markup = {"keyboard": [[{"text": self.get_text(lang, 'phone_btn'), "request_contact": True}]], "resize_keyboard": True}
                send_msg(chat_id, self.get_text(lang, 'phone_req'), markup)
            return

        # 2. الكابتشا
        if now - captcha_time > 3600:
            self.send_captcha(chat_id, lang)
            return

        # 3. التحقق من القنوات الإجبارية
        c.execute("SELECT url, ch_id FROM channels WHERE type = 'main'")
        for ch_url, ch_id in c.fetchall():
            if not check_sub(user_id, ch_id):
                markup = {"inline_keyboard": [[{"text": "📢 Join / اشترك", "url": ch_url}], [{"text": "✅ Check / تحقق", "callback_data": "check_main_sub"}]]}
                send_msg(chat_id, self.get_text(lang, 'sub_req'), markup)
                return

        # ================= معالجة أزرار الكيبورد السفلي =================
        if text == self.get_text(lang, 'btn_refresh'):
            self.send_main_menu(chat_id, user_id, c, conn, lang)
            return
            
        elif text == self.get_text(lang, 'btn_lang'):
            new_lang = 'en' if lang == 'ar' else 'ar'
            c.execute("UPDATE users SET lang = ? WHERE user_id = ?", (new_lang, user_id))
            conn.commit()
            send_msg(chat_id, "🌐 Language Updated / تم تحديث اللغة", self.get_reply_keyboard(new_lang))
            self.send_main_menu(chat_id, user_id, c, conn, new_lang)
            return
            
        elif text == self.get_text(lang, 'btn_withdraw'):
            self.update_mining(user_id, c, conn)
            c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            current_bal = float(c.fetchone()[0] or 0)
            if current_bal < MIN_WITHDRAW:
                send_msg(chat_id, self.get_text(lang, 'withdraw_err', min=MIN_WITHDRAW))
            else:
                c.execute("UPDATE users SET state = 'wait_wallet' WHERE user_id = ?", (user_id,))
                conn.commit()
                send_msg(chat_id, self.get_text(lang, 'withdraw_req'))
            return
            
        elif text == self.get_text(lang, 'btn_team'):
            c.execute("SELECT ref_count FROM users WHERE user_id = ?", (user_id,))
            refs = int(c.fetchone()[0] or 0)
            link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
            send_msg(chat_id, self.get_text(lang, 'team_msg', refs=refs, link=link))
            return
            
        elif text == self.get_text(lang, 'btn_tasks'):
            c.execute("SELECT id, reward FROM shortlinks")
            links = c.fetchall()
            if not links:
                send_msg(chat_id, "No tasks / لا توجد مهام حالياً")
                return
            btns = [[{"text": f"🔗 Task (+{float(l[1] or 0):.8f})", "callback_data": f"do_link_{l[0]}"}] for l in links]
            send_msg(chat_id, self.get_text(lang, 'task_msg'), {"inline_keyboard": btns})
            return

        # ================= معالجة إدخال النصوص والحالات =================
        if state == 'wait_wallet':
            # إلغاء إذا ضغط على أي زر من القائمة بدل إدخال المحفظة
            if text in [self.get_text(lang, k) for k in ['btn_refresh', 'btn_withdraw', 'btn_team', 'btn_tasks', 'btn_lang']]:
                c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
                conn.commit()
                return
                
            for admin in c.execute("SELECT user_id FROM admins").fetchall():
                send_msg(admin[0], f"🔔 <b>طلب سحب!</b>\n👤 آيدي: <code>{user_id}</code>\n💰 الرصيد: <code>{bal_float:.8f}</code>\n🏦 المحفظة:\n<code>{text}</code>")
            
            c.execute("UPDATE users SET balance = 0, state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, self.get_text(lang, 'withdraw_done'))
            return

        elif state.startswith('wait_pass_'):
            if text in [self.get_text(lang, k) for k in ['btn_refresh', 'btn_withdraw', 'btn_team', 'btn_tasks', 'btn_lang']]:
                c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
                conn.commit()
                return

            link_id = int(state.split('_')[2])
            c.execute("SELECT password, reward FROM shortlinks WHERE id = ?", (link_id,))
            link = c.fetchone()
            if link and text.strip() == link[0]:
                c.execute("UPDATE users SET balance = balance + ?, state = 'idle' WHERE user_id = ?", (float(link[1] or 0), user_id))
                conn.commit()
                send_msg(chat_id, self.get_text(lang, 'task_ok', reward=float(link[1] or 0)))
            else:
                c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
                conn.commit()
                send_msg(chat_id, self.get_text(lang, 'task_err'))
            return

        # أوامر الإدارة الخاصة بالمالك
        elif state == 'admin_wait_bal_id' and is_admin:
            try:
                target_id = int(text)
                c.execute("UPDATE users SET state = ? WHERE user_id = ?", (f'admin_wait_bal_amt_{target_id}', user_id))
                conn.commit()
                send_msg(chat_id, f"✅ تم تحديد المستخدم: {target_id}\nأرسل الآن المبلغ المراد إضافته:")
            except: send_msg(chat_id, "❌ الآيدي غير صحيح.")
            return
            
        elif state.startswith('admin_wait_bal_amt_') and is_admin:
            target_id = int(state.split('_')[4])
            try:
                amount = float(text)
                c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_id))
                c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
                conn.commit()
                send_msg(chat_id, f"✅ تمت الإضافة.")
                send_msg(target_id, f"🎉 <b>إهداء من الإدارة!</b>\nتمت إضافة <code>{amount:.8f}</code> DOGE إلى رصيدك.")
            except: send_msg(chat_id, "❌ المبلغ غير صحيح.")
            return

        if text == "/start":
            send_msg(chat_id, "✅", self.get_reply_keyboard(lang)) # إظهار الكيبورد السفلي
            self.send_main_menu(chat_id, user_id, c, conn, lang)
        elif text == "/admin" and is_admin:
            self.send_admin_panel(chat_id, lang)

        conn.close()

    def handle_callback(self, cq):
        chat_id = cq['message']['chat']['id']
        user_id = cq['from']['id']
        data = cq['data']
        msg_id = cq['message']['message_id']
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT lang, referrer_id, captcha_time FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        
        if not row:
            send_msg(chat_id, "⚠️ يرجى إرسال /start من جديد لبدء التعدين.")
            conn.close()
            return
            
        lang, ref_id, cap_time = row
        is_admin = c.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)).fetchone() is not None

        if data == "cap_ok":
            now = int(time.time())
            if cap_time == 0 and ref_id != 0:
                c.execute("UPDATE users SET speed = speed * 1.3, ref_count = ref_count + 1 WHERE user_id = ?", (ref_id,))
                ref_lang = c.execute("SELECT lang FROM users WHERE user_id = ?", (ref_id,)).fetchone()
                if ref_lang: send_msg(ref_id, self.get_text(ref_lang[0], 'ref_notify'))

            c.execute("UPDATE users SET captcha_time = ? WHERE user_id = ?", (now, user_id))
            conn.commit()
            
            # إخفاء أزرار الكابتشا وإظهار الكيبورد السفلي
            call_api("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
            send_msg(chat_id, "✅", self.get_reply_keyboard(lang))
            self.send_main_menu(chat_id, user_id, c, conn, lang)
            
        elif data == "cap_fail":
            call_api("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
            send_msg(chat_id, self.get_text(lang, 'captcha_fail'))
            self.send_captcha(chat_id, lang)
            
        elif data == "check_main_sub":
            self.send_main_menu(chat_id, user_id, c, conn, lang)
            
        elif data.startswith("do_link_"):
            link_id = int(data.split("_")[2])
            c.execute("UPDATE users SET state = ? WHERE user_id = ?", (f"wait_pass_{link_id}", user_id))
            conn.commit()
            send_msg(chat_id, "🔑 أرسل كلمة السر الآن هنا:")

        elif data == "admin_add_bal" and is_admin:
            c.execute("UPDATE users SET state = 'admin_wait_bal_id' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "💰 أرسل <b>الآيدي (ID)</b>:")

        conn.close()

    def send_captcha(self, chat_id, lang):
        btns = [{"text": "🔹", "callback_data": "cap_fail"} for _ in range(3)]
        btns.insert(random.randint(0, 3), {"text": "🔴", "callback_data": "cap_ok"})
        send_msg(chat_id, self.get_text(lang, 'captcha_msg'), {"inline_keyboard": [btns]})

    def update_mining(self, user_id, cursor, conn):
        try:
            now = int(time.time())
            cursor.execute("SELECT balance, speed, last_update FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                bal = float(row[0] or 0)
                speed = float(row[1] or 0.0000000115)
                last = int(row[2]) if row[2] else now
                earned = (now - last) * speed
                cursor.execute("UPDATE users SET balance = ?, last_update = ? WHERE user_id = ?", (bal + earned, now, user_id))
                conn.commit()
        except: pass

    def send_main_menu(self, chat_id, user_id, cursor, conn, lang):
        self.update_mining(user_id, cursor, conn)
        cursor.execute("SELECT balance, speed, ref_count FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        bal = float(row[0] or 0)
        speed = float(row[1] or 0.0000000115)
        refs = int(row[2] or 0)
        text = self.get_text(lang, 'main_menu', balance=bal, speed=speed*86400, refs=refs)
        
        # الرسالة الأساسية بدون أزرار شفافة (لأن الأزرار تحت في الكيبورد)
        send_msg(chat_id, text)

    def send_admin_panel(self, chat_id, lang):
        # هذه هي الأزرار العلوية الشفافة الخاصة بالمالك فقط
        btns = [
            [{"text": "💰 زيادة رصيد مستخدم", "callback_data": "admin_add_bal"}],
            [{"text": "📢 إذاعة للجميع", "callback_data": "admin_broadcast"}],
            [{"text": "➕ إضافة قناة إجبارية", "callback_data": "add_main_ch"}],
            [{"text": "🔗 إضافة رابط وكلمة سر", "callback_data": "add_shortlink"}],
            [{"text": "🔘 إضافة زر مخصص", "callback_data": "add_custom_btn"}]
        ]
        send_msg(chat_id, self.get_text(lang, 'admin_panel'), {"inline_keyboard": btns})
        
