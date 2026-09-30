from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import sqlite3
import time
import random
import re

# ================= الإعدادات الأساسية =================
TOKEN = "8960593021:AAFkF-8Cvt_jsOHJmNUyBGWMvzmE0hIbMbk"
OWNER_ID = 6610111288
BOT_USERNAME = "Dogcoinibot"
DB_PATH = "/tmp/doge_bot_v2.db"
MIN_WITHDRAW = 0.01

# ================= قاموس اللغات (Localization) =================
LANG = {
    'ar': {
        'captcha_msg': "🤖 <b>نظام الحماية ضد الروبوتات:</b>\n\nيجب عليك الضغط على الرمز المختلف (🔴) للبدء في جمع Dogecoin.",
        'captcha_ok': "✅ تم التحقق البشري بنجاح! مرحباً بك في المنجم.",
        'captcha_fail': "❌ فشل التحقق! يرجى التركيز والمحاولة مجدداً.",
        'phone_req': "🔒 <b>خطوة أمنية أخيرة:</b>\n\nلضمان عدم استخدام حسابات وهمية، يرجى مشاركة رقم هاتفك عبر الزر أدناه.",
        'phone_btn': "📱 مشاركة جهة الاتصال (إجباري)",
        'phone_err': "❌ عذراً، الأرقام من هذه الدولة محظورة في نظامنا.",
        'sub_req': "⚠️ <b>تنبيه هام!</b>\n\nيجب عليك الاشتراك في قنواتنا الرسمية أولاً لتتمكن من تشغيل التعدين وسحب الأرباح.",
        'sub_check_btn': "✅ تحقق من الاشتراك",
        'sub_join_btn': "📢 اضغط هنا للاشتراك",
        'main_menu': "⛏️ <b>مركز تعدين Dogecoin السحابي</b>\n\n💰 الرصيد المباشر:\n<code>{balance:.8f}</code> <b>DOGE</b>\n\n⚡ سرعة التعدين: <code>{speed:.8f}</code> DOGE/يوم\n👥 أعضاء فريقك: <code>{refs}</code> عضو\n\n<i>العداد يعمل تلقائياً، اضغط تحديث لجمع تعدينك.</i>",
        'btn_refresh': "🔄 تحديث وجمع الأرباح",
        'btn_withdraw': "💸 سحب الرصيد",
        'btn_team': "👥 فريقك (زيادة 30%)",
        'btn_tasks': "🔗 المهام والروابط المربحة",
        'btn_lang': "🌐 English",
        'team_msg': "👥 <b>نظام الإحالات الخاص بك:</b>\n\nكل شخص تدعوه ويكمل التحقق يمنحك زيادة <b>+30%</b> في سرعة التعدين.\n\n📊 <b>إحصائياتك:</b>\n- الأعضاء النشطين: <code>{refs}</code>\n\n🔗 <b>رابط الدعوة الخاص بك:</b>\n<code>{link}</code>",
        'withdraw_err': "❌ عذراً، رصيدك الحالي أقل من الحد الأدنى للسحب وهو ({min} DOGE).",
        'withdraw_req': "💸 <b>طلب سحب جديد:</b>\n\nأرسل الآن عنوان محفظة <b>Dogecoin (FaucetPay)</b> الخاصة بك:",
        'withdraw_done': "✅ <b>تم استلام طلبك!</b>\nسيتم تحويل الرصيد إلى محفظتك بعد مراجعة الحساب.",
        'ref_notify': "🎉 <b>أخبار رائعة!</b>\nشخص جديد سجل عبر رابطك وتخطى الكابتشا بنجاح. تمت زيادة سرعة تعدينك بنسبة 30%!",
        'task_msg': "🔗 <b>تخطي الروابط:</b>\n\n1. اضغط على الرابط وتخطى الإعلانات.\n2. انسخ كلمة السر الخفية من الصفحة الأخيرة.\n3. أرسل كلمة السر هنا للحصول على المكافأة.",
        'task_ok': "🎉 <b>إجابة صحيحة!</b> تمت إضافة {reward} DOGE لرصيدك.",
        'task_err': "❌ <b>كلمة السر خاطئة!</b> حاول مرة أخرى.",
        'admin_panel': "👑 <b>لوحة تحكم المالك المطلقة:</b>\nاختر الإجراء المطلوب من القائمة أدناه:",
    },
    'en': {
        'captcha_msg': "🤖 <b>Anti-Bot Security:</b>\n\nPlease click on the different symbol (🔴) to start mining Dogecoin.",
        'captcha_ok': "✅ Human verification successful! Welcome to the mine.",
        'captcha_fail': "❌ Verification failed! Please focus and try again.",
        'phone_req': "🔒 <b>Final Security Step:</b>\n\nTo prevent fake accounts, please share your phone number using the button below.",
        'phone_btn': "📱 Share Contact (Required)",
        'phone_err': "❌ Sorry, phone numbers from this region are blocked.",
        'sub_req': "⚠️ <b>Important Notice!</b>\n\nYou must subscribe to our official channels first to enable mining and withdrawals.",
        'sub_check_btn': "✅ Check Subscription",
        'sub_join_btn': "📢 Click to Join",
        'main_menu': "⛏️ <b>Dogecoin Cloud Mining Center</b>\n\n💰 Live Balance:\n<code>{balance:.8f}</code> <b>DOGE</b>\n\n⚡ Mining Speed: <code>{speed:.8f}</code> DOGE/Day\n👥 Team Members: <code>{refs}</code> active\n\n<i>Miner runs automatically, click refresh to collect.</i>",
        'btn_refresh': "🔄 Refresh & Collect",
        'btn_withdraw': "💸 Withdraw Funds",
        'btn_team': "👥 Your Team (+30%)",
        'btn_tasks': "🔗 Profitable Tasks",
        'btn_lang': "🌐 العربية",
        'team_msg': "👥 <b>Your Referral System:</b>\n\nEvery person you invite who completes verification gives you a <b>+30%</b> mining speed boost.\n\n📊 <b>Your Stats:</b>\n- Active Members: <code>{refs}</code>\n\n🔗 <b>Your Invite Link:</b>\n<code>{link}</code>",
        'withdraw_err': "❌ Sorry, your balance is below the minimum withdrawal limit ({min} DOGE).",
        'withdraw_req': "💸 <b>New Withdrawal Request:</b>\n\nPlease send your <b>Dogecoin (FaucetPay)</b> wallet address now:",
        'withdraw_done': "✅ <b>Request Received!</b>\nFunds will be sent to your wallet after account review.",
        'ref_notify': "🎉 <b>Great News!</b>\nA new user joined via your link and passed the captcha. Your mining speed increased by 30%!",
        'task_msg': "🔗 <b>Shortlink Tasks:</b>\n\n1. Click the link and skip ads.\n2. Copy the hidden password from the last page.\n3. Send the password here to get your reward.",
        'task_ok': "🎉 <b>Correct Password!</b> {reward} DOGE added to your balance.",
        'task_err': "❌ <b>Wrong Password!</b> Try again.",
        'admin_panel': "👑 <b>Absolute Owner Panel:</b>\nSelect an action from the menu below:",
    }
}

# ================= قاعدة البيانات =================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # جدول المستخدمين
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY, phone TEXT, balance REAL DEFAULT 0.0,
                    speed REAL DEFAULT 0.0000000115, last_update INTEGER,
                    captcha_time INTEGER DEFAULT 0, referrer_id INTEGER DEFAULT 0,
                    ref_count INTEGER DEFAULT 0, state TEXT DEFAULT 'idle', lang TEXT DEFAULT 'ar')''')
    # جدول المشرفين
    c.execute('''CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)''')
    c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (OWNER_ID,))
    # جداول المهام والقنوات
    c.execute('''CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, ch_id TEXT, type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS shortlinks (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, password TEXT, reward REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS custom_btns (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT)''')
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
    payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if markup: payload["reply_markup"] = markup
    call_api("editMessageText", payload)

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
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            if 'message' in data: self.handle_message(data['message'])
            elif 'callback_query' in data: self.handle_callback(data['callback_query'])
            self.send_response(200)
            self.end_headers()
        except:
            self.send_response(500)
            self.end_headers()
        return

    def get_text(self, lang, key, **kwargs):
        text = LANG.get(lang, LANG['ar']).get(key, "")
        if kwargs: text = text.format(**kwargs)
        return text

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

        # 1. التحقق من الرقم 
        if not phone:
            if 'contact' in msg and msg['contact']['user_id'] == user_id:
                p = msg['contact']['phone_number']
                if not p.startswith('+'): p = '+' + p
                if re.match(r'^\+(1|3|4|61)', p) and not p.startswith('+7'):
                    send_msg(chat_id, self.get_text(lang, 'phone_err'))
                    return
                c.execute("UPDATE users SET phone = ? WHERE user_id = ?", (p, user_id))
                conn.commit()
                self.send_captcha(chat_id, lang)
            else:
                markup = {"keyboard": [[{"text": self.get_text(lang, 'phone_btn'), "request_contact": True}]], "resize_keyboard": True}
                send_msg(chat_id, self.get_text(lang, 'phone_req'), markup)
            return

        # 2. نظام الكابتشا الخفي
        if now - captcha_time > 3600:
            self.send_captcha(chat_id, lang)
            return

        # 3. التحقق من القنوات الإجبارية
        c.execute("SELECT url, ch_id FROM channels WHERE type = 'main'")
        main_channels = c.fetchall()
        for ch_url, ch_id in main_channels:
            if not check_sub(user_id, ch_id):
                markup = {"inline_keyboard": [[{"text": self.get_text(lang, 'sub_join_btn'), "url": ch_url}], 
                                            [{"text": self.get_text(lang, 'sub_check_btn'), "callback_data": "check_main_sub"}]]}
                send_msg(chat_id, self.get_text(lang, 'sub_req'), markup)
                return

        # 4. معالجة الحالات (State Machine)
        if state == 'wait_wallet':
            # الإشعار المباشر للمالك
            c.execute("SELECT user_id FROM admins")
            for admin in c.fetchall():
                send_msg(admin[0], f"🔔 <b>طلب سحب عاجل!</b>\n\n👤 المستخدم: <code>{user_id}</code>\n💰 الرصيد: <code>{balance:.8f}</code> DOGE\n🏦 المحفظة:\n<code>{text}</code>")
            
            c.execute("UPDATE users SET balance = 0, state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, self.get_text(lang, 'withdraw_done'))
            self.send_main_menu(chat_id, user_id, c, lang)
            return

        elif state.startswith('wait_pass_'):
            link_id = int(state.split('_')[2])
            c.execute("SELECT password, reward FROM shortlinks WHERE id = ?", (link_id,))
            link = c.fetchone()
            if link and text.strip() == link[0]:
                c.execute("UPDATE users SET balance = balance + ?, state = 'idle' WHERE user_id = ?", (link[1], user_id))
                conn.commit()
                send_msg(chat_id, self.get_text(lang, 'task_ok', reward=link[1]))
            else:
                c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
                conn.commit()
                send_msg(chat_id, self.get_text(lang, 'task_err'))
            self.send_main_menu(chat_id, user_id, c, lang)
            return

        # 5. أوامر تحكم المالك المطلقة
        elif state == 'admin_wait_bal_id' and is_admin:
            try:
                target_id = int(text)
                c.execute("UPDATE users SET state = ? WHERE user_id = ?", (f'admin_wait_bal_amt_{target_id}', user_id))
                conn.commit()
                send_msg(chat_id, f"✅ تم تحديد المستخدم: {target_id}\nأرسل الآن المبلغ المراد إضافته (مثال: 100.5):")
            except:
                send_msg(chat_id, "❌ الآيدي غير صحيح.")
            return
            
        elif state.startswith('admin_wait_bal_amt_') and is_admin:
            target_id = int(state.split('_')[4])
            try:
                amount = float(text)
                c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_id))
                c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
                conn.commit()
                send_msg(chat_id, f"✅ تم إضافة {amount:.8f} DOGE إلى رصيد المستخدم {target_id} بنجاح.")
                send_msg(target_id, f"🎉 <b>إهداء من الإدارة!</b>\nتمت إضافة <code>{amount:.8f}</code> DOGE إلى رصيدك.")
            except:
                send_msg(chat_id, "❌ المبلغ غير صحيح.")
            return

        elif text == "/start":
            self.send_main_menu(chat_id, user_id, c, lang)
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
        lang, ref_id, cap_time = c.fetchone()
        
        c.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
        is_admin = c.fetchone() is not None

        if data == "cap_ok":
            now = int(time.time())
            # تفعيل مكافأة الإحالة فقط بعد نجاح الكابتشا لأول مرة
            if cap_time == 0 and ref_id != 0:
                c.execute("UPDATE users SET speed = speed * 1.3, ref_count = ref_count + 1 WHERE user_id = ?", (ref_id,))
                c.execute("SELECT lang FROM users WHERE user_id = ?", (ref_id,))
                ref_lang = c.fetchone()
                if ref_lang:
                    send_msg(ref_id, self.get_text(ref_lang[0], 'ref_notify'))

            c.execute("UPDATE users SET captcha_time = ? WHERE user_id = ?", (now, user_id))
            conn.commit()
            edit_msg(chat_id, msg_id, self.get_text(lang, 'captcha_ok'))
            self.send_main_menu(chat_id, user_id, c, lang)
            
        elif data == "cap_fail":
            edit_msg(chat_id, msg_id, self.get_text(lang, 'captcha_fail'))
            self.send_captcha(chat_id, lang)
            
        elif data == "toggle_lang":
            new_lang = 'en' if lang == 'ar' else 'ar'
            c.execute("UPDATE users SET lang = ? WHERE user_id = ?", (new_lang, user_id))
            conn.commit()
            self.update_mining(user_id, c)
            self.edit_main_menu(chat_id, user_id, msg_id, c, new_lang)
            
        elif data == "refresh_mine" or data == "check_main_sub":
            self.update_mining(user_id, c)
            conn.commit()
            self.edit_main_menu(chat_id, user_id, msg_id, c, lang)
            
        elif data == "req_withdraw":
            self.update_mining(user_id, c)
            c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            bal = c.fetchone()[0]
            if bal < MIN_WITHDRAW:
                call_api("answerCallbackQuery", {"callback_query_id": cq['id'], "text": self.get_text(lang, 'withdraw_err', min=MIN_WITHDRAW), "show_alert": True})
            else:
                c.execute("UPDATE users SET state = 'wait_wallet' WHERE user_id = ?", (user_id,))
                conn.commit()
                send_msg(chat_id, self.get_text(lang, 'withdraw_req'))

        elif data == "show_team":
            c.execute("SELECT ref_count FROM users WHERE user_id = ?", (user_id,))
            refs = c.fetchone()[0]
            link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
            send_msg(chat_id, self.get_text(lang, 'team_msg', refs=refs, link=link))

        elif data == "show_tasks":
            c.execute("SELECT id, reward FROM shortlinks")
            links = c.fetchall()
            btns = [[{"text": f"🔗 Task (+{l[1]:.8f} DOGE)", "callback_data": f"do_link_{l[0]}"}]] for l in links]
            send_msg(chat_id, self.get_text(lang, 'btn_tasks'), {"inline_keyboard": btns} if btns else None)

        elif data.startswith("do_link_"):
            link_id = data.split("_")[2]
            c.execute("UPDATE users SET state = ? WHERE user_id = ?", (f"wait_pass_{link_id}", user_id))
            conn.commit()
            send_msg(chat_id, self.get_text(lang, 'task_msg'))

        # ================= أوامر الإدارة =================
        elif data == "admin_panel" and is_admin:
            self.send_admin_panel(chat_id, lang)
            
        elif data == "admin_add_bal" and is_admin:
            c.execute("UPDATE users SET state = 'admin_wait_bal_id' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "💰 أرسل <b>الآيدي (ID)</b> للمستخدم الذي تريد زيادة رصيده:")

        conn.close()

    # ================= الدوال المساعدة =================
    def send_captcha(self, chat_id, lang):
        btns = [{"text": "🔹", "callback_data": "cap_fail"} for _ in range(3)]
        btns.insert(random.randint(0, 3), {"text": "🔴", "callback_data": "cap_ok"})
        send_msg(chat_id, self.get_text(lang, 'captcha_msg'), {"inline_keyboard": [btns]})

    def update_mining(self, user_id, cursor):
        now = int(time.time())
        cursor.execute("SELECT balance, speed, last_update FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            bal, speed, last = row
            earned = (now - last) * speed
            cursor.execute("UPDATE users SET balance = ?, last_update = ? WHERE user_id = ?", (bal + earned, now, user_id))

    def get_main_menu(self, user_id, cursor, lang):
        btns = [
            [{"text": self.get_text(lang, 'btn_refresh'), "callback_data": "refresh_mine"}],
            [{"text": self.get_text(lang, 'btn_withdraw'), "callback_data": "req_withdraw"}, 
             {"text": self.get_text(lang, 'btn_team'), "callback_data": "show_team"}],
            [{"text": self.get_text(lang, 'btn_tasks'), "callback_data": "show_tasks"},
             {"text": self.get_text(lang, 'btn_lang'), "callback_data": "toggle_lang"}]
        ]
        cursor.execute("SELECT name, url FROM custom_btns")
        for btn in cursor.fetchall(): btns.append([{"text": btn[0], "url": btn[1]}])
        
        cursor.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,))
        if cursor.fetchone(): btns.append([{"text": "⚙️ لوحة الإدارة المطلقة", "callback_data": "admin_panel"}])
        return {"inline_keyboard": btns}

    def send_main_menu(self, chat_id, user_id, cursor, lang):
        self.update_mining(user_id, cursor)
        cursor.execute("SELECT balance, speed, ref_count FROM users WHERE user_id = ?", (user_id,))
        bal, speed, refs = cursor.fetchone()
        text = self.get_text(lang, 'main_menu', balance=bal, speed=speed*86400, refs=refs)
        send_msg(chat_id, text, self.get_main_menu(user_id, cursor, lang))

    def edit_main_menu(self, chat_id, user_id, msg_id, cursor
