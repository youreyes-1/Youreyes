from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import sqlite3
import time
import random
import re
import traceback

# ================= الإعدادات الأساسية =================
TOKEN = "8960593021:AAFEn0HioVC4K2S_LkJWVgqJVMYYJt-xF4Q"
OWNER_ID = 6610111288
BOT_USERNAME = "Dogcoinibot"
DB_PATH = "/tmp/doge_final_v8.db"

LANG = {
    'ar': {
        'btn_refresh': "🔄 تحديث الأرباح",
        'btn_withdraw': "💸 سحب الرصيد",
        'btn_team': "👥 فريقك (+30%)",
        'btn_tasks': "🔗 المهام والروابط",
        'btn_speed_ch': "📢 قنوات زيادة السرعة",
        'btn_about': "🖥️ عتاد التعدين",
        'btn_stats': "📊 إحصائيات المنجم",
        'btn_calc': "🧮 حاسبة الأرباح",
        'btn_support': "📞 الدعم الفني",
        'btn_lang': "🌐 English",
        'btn_admin': "👑 الإدارة (للمشرفين)",
        'captcha_msg': "🤖 <b>نظام الحماية (Anti-Bot):</b>\n\nاضغط على الرمز المختلف (🔴) للبدء في جمع Dogecoin.",
        'captcha_ok': "تم التحقق البشري بنجاح! يرجى الاشتراك في القناة الرسمية أدناه للمتابعة.",
        'captcha_fail': "❌ فشل التحقق الأمني! حاول مجدداً.",
        'sub_req': "⚠️ <b>شرط أساسي لفتح البوت!</b>\n\nيجب عليك الاشتراك في قناتنا الرسمية أدناه لتفعيل حسابك والبدء في تعدين Dogecoin:",
        'main_menu': "⛏ <b>خوادم التعدين النشطة</b>\n\n💰 الرصيد المباشر: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ قوة التعدين: <code>{speed:.8f}</code> DOGE/يوم\n👥 أعضاء الفريق: <code>{refs}</code>\n\n<i>🟢 حالة الخادم: متصل ومستقر.</i>",
        'team_msg': "👥 <b>برنامج الشركاء (Referral):</b>\n\nكل عضو تدعوه يزيد سرعة تعدينك بنسبة <b>30%</b> فور تجاوزه الكابتشا.\n\n📊 فريقك: <code>{refs}</code> عضو\n🔗 رابط الدعوة الخاص بك:\n<code>{link}</code>",
        'withdraw_err': "❌ رصيدك الحالي أقل من الحد الأدنى للسحب ({min} DOGE).",
        'withdraw_req': "💸 <b>بوابة السحب الآمنة:</b>\nأرسل الآن عنوان محفظة <b>Dogecoin (FaucetPay)</b> الخاصة بك لجدولة الدفعة:",
        'withdraw_done': "✅ <b>تم استلام طلب السحب!</b>\nالطلب قيد المراجعة المالية، ستصلك الدفعة قريباً.",
        'ref_notify': "🎉 <b>أخبار ممتازة!</b>\nسجل عضو جديد عبر رابطك وتجاوز الكابتشا. تمت زيادة سرعة تعدينك بنسبة 30%!",
        'calc_text': "🧮 <b>حاسبة العوائد والأرباح التراكمية:</b>\n\n⚡ <b>قوة الإحالات والمكافآت اليومية:</b>\n• إذا قمت بدعوة <b>10 إلى 15 شخصاً</b> فقط = سرعة تعدين تتضاعف 450%.\n• إذا وصلت إلى <b>30 - 40 إحالة نشطة</b> = ستحقق أرباحاً يومية مباشرة تتراوح بين <b>5$ إلى 8$ دولار</b> (ما يعادل 35 - 55 DOGE يومياً) قابلة للسحب المباشر دون توقف!\n\n💡 <i>نصيحة ذهبية: انسخ رابطك من زر (فريقك) وانشره في مجموعات التواصل وابدأ بناء دخلك السلبي الآن!</i>",
        'about_text': "🖥️ <b>البنية التحتية لمنظومة التعدين:</b>\n\nتعتمد مزارعنا على أحدث مصفوفات المعالجة الرسومية <b>NVIDIA RTX 4090</b> المربوطة بوحدات تعدين متخصصة من طراز <b>Bitmain Antminer L7</b> لفك تشفير خوارزمية Scrypt المخصصة لعملة Dogecoin.\n\nتدار الخوادم بأنظمة تبريد سائل مغلقة ذات كفاءة طاقية فائقة تضمن استقرار استخراج الكتل على مدار 24 ساعة ومنح عوائد يومية مستمرة لمستخدمينا المشتركين بالشبكة.",
        'stats_text': "📊 <b>إحصائيات الشبكة المباشرة:</b>\n\n👤 عمال التعدين النشطين: <code>{miners}</code>\n⚡ قوة الهاش الإجمالية: <code>9.2 GH/s Scrypt</code>\n💸 إجمالي السحوبات المؤكدة اليوم: <code>1,450 DOGE</code>\n🟢 كفاءة الطاقة والتشغيل: <code>{eff}%</code>",
        'support_text': "📞 <b>مركز خدمة العملاء:</b>\n\nنظراً للضغط المرتفع، يستغرق الرد من فريق الدعم من 24 إلى 48 ساعة.",
        'admin_panel': "👑 <b>مركز القيادة (المالك والمشرفين):</b>\nاختر العملية المطلوبة:"
    },
    'en': {
        'btn_refresh': "🔄 Refresh Data",
        'btn_withdraw': "💸 Withdraw Funds",
        'btn_team': "👥 Your Team",
        'btn_tasks': "🔗 Shortlink Tasks",
        'btn_speed_ch': "📢 Speed Channels",
        'btn_about': "🖥️ Mining Rig Hardware",
        'btn_stats': "📊 Network Stats",
        'btn_calc': "🧮 Profit Calculator",
        'btn_support': "📞 Support",
        'btn_lang': "🌐 العربية",
        'btn_admin': "👑 Admin Panel",
        'captcha_msg': "🤖 <b>Anti-Bot System:</b>\n\nClick the unique symbol (🔴) to authenticate.",
        'captcha_ok': "Human verification successful! Please join our official channel below.",
        'captcha_fail': "❌ Verification failed! Please try again.",
        'sub_req': "⚠️ <b>Action Required!</b>\n\nYou must join our official channel below to unlock and activate your miner:",
        'main_menu': "⛏ <b>Active Mining Servers</b>\n\n💰 Live Balance: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ Hash Power: <code>{speed:.8f}</code> DOGE/Day\n👥 Team Size: <code>{refs}</code>\n\n<i>🟢 Server Status: Online & Stable.</i>",
        'team_msg': "👥 <b>Partner Program:</b>\n\nEarn a <b>30%</b> mining speed boost for every verified referral.\n\n📊 Team Members: <code>{refs}</code>\n🔗 Your Referral Link:\n<code>{link}</code>",
        'withdraw_err': "❌ Balance is below the minimum threshold ({min} DOGE).",
        'withdraw_req': "💸 <b>Secure Withdrawal:</b>\nSend your <b>Dogecoin (FaucetPay)</b> wallet address:",
        'withdraw_done': "✅ <b>Request Logged!</b>\nYour payout is under review.",
        'ref_notify': "🎉 <b>Great News!</b>\nA new user joined via your link. Speed increased by 30%!",
        'calc_text': "🧮 <b>Profit Calculator:</b>\n\n• 10-15 Referrals = 450% Boost.\n• 30-40 Referrals = <b>$5 to $8 USD daily</b> in DOGE automatically!\n\n<i>Share your link to maximize income.</i>",
        'about_text': "🖥️ <b>Hardware Infrastructure:</b>\n\nPowered by massive arrays of <b>NVIDIA RTX 4090</b> rigs paired with high-efficiency <b>Antminer L7</b> units operating Scrypt algorithms under liquid cooling.",
        'stats_text': "📊 <b>Live Network Stats:</b>\n\n👤 Active Miners: <code>{miners}</code>\n⚡ Hashrate: <code>9.2 GH/s Scrypt</code>\n💸 Paid Today: <code>1,450 DOGE</code>\n🟢 Rig Uptime: <code>{eff}%</code>",
        'support_text': "📞 <b>Customer Support:</b>\n\nResponse time is currently 24-48 hours.",
        'admin_panel': "👑 <b>Command Center:</b>\nSelect an administrative action:"
    }
}

# ================= قاعدة البيانات =================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0.0,
                    speed REAL DEFAULT 0.0000000115, last_update INTEGER,
                    captcha_passed INTEGER DEFAULT 0, referrer_id INTEGER DEFAULT 0,
                    ref_count INTEGER DEFAULT 0, state TEXT DEFAULT 'idle', lang TEXT DEFAULT 'ar')''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)''')
    c.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (OWNER_ID,))
    c.execute('''CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT, ch_id TEXT, type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS shortlinks (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, url TEXT, password TEXT, reward REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS claimed_tasks (user_id INTEGER, task_id INTEGER, claimed_at INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS joined_speed_channels (user_id INTEGER, ch_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('min_withdraw', '0.01')")
    conn.commit()
    conn.close()

def get_min_withdraw():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = 'min_withdraw'")
    row = c.fetchone()
    conn.close()
    return float(row[0]) if row else 0.01

def call_api(method, payload):
    api_url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    req = urllib.request.Request(api_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        res = urllib.request.urlopen(req, timeout=6)
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
    if not channel_id:
        return True
    res = call_api("getChatMember", {"chat_id": channel_id, "user_id": user_id})
    if res and res.get('ok'):
        return res['result']['status'] in ['member', 'administrator', 'creator']
    return False

def get_text(lang, key, **kwargs):
    text = LANG.get(lang, LANG['ar']).get(key, "")
    if kwargs:
        text = text.format(**kwargs)
    return text

def get_dynamic_stats():
    now_ts = int(time.time())
    launch_ts = 1788220800
    days_passed = max(0, (now_ts - launch_ts) // 86400)
    
    total_growth = 0
    for d in range(min(days_passed, 365)):
        random.seed(999 + d)
        total_growth += random.randint(300, 450)
        
    miners = 16780 + total_growth
    
    random.seed(now_ts // 1800)
    eff = round(random.uniform(96.2, 98.7), 2)
    random.seed()
    return f"{miners:,}", eff

def get_reply_keyboard(lang, is_admin):
    kb = [
        [{"text": get_text(lang, 'btn_refresh')}],
        [{"text": get_text(lang, 'btn_withdraw')}, {"text": get_text(lang, 'btn_team')}],
        [{"text": get_text(lang, 'btn_tasks')}, {"text": get_text(lang, 'btn_speed_ch')}],
        [{"text": get_text(lang, 'btn_calc')}, {"text": get_text(lang, 'btn_stats')}],
        [{"text": get_text(lang, 'btn_about')}, {"text": get_text(lang, 'btn_support')}],
        [{"text": get_text(lang, 'btn_lang')}]
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
    min_w = get_min_withdraw()
    btns = [
        [{"text": "💰 زيادة رصيد مستخدم", "callback_data": "admin_add_bal"}, {"text": "📢 إذاعة للجميع", "callback_data": "admin_broadcast"}],
        [{"text": f"⚙️ تعديل الحد الأدنى للسحب ({min_w} DOGE)", "callback_data": "admin_set_min_w"}],
        [{"text": "👥 مراقبة المحتالين (>10 إحالة)", "callback_data": "admin_top_refs"}],
        [{"text": "➕ إضافة قناة إجبارية", "callback_data": "admin_add_main_ch"}, {"text": "📢 إضافة قناة مهام (+10%)", "callback_data": "admin_add_speed_ch"}],
        [{"text": "🔗 إضافة مهمة رابط مختصر", "callback_data": "admin_add_shortlink"}],
        [{"text": "🗑️ إدارة وحذف القنوات", "callback_data": "admin_manage_channels"}, {"text": "🗑️ إدارة وحذف المهام", "callback_data": "admin_manage_tasks"}],
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

    is_admin = c.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)).fetchone() is not None or user_id == OWNER_ID

    if is_admin:
        c.execute("INSERT OR IGNORE INTO users (user_id, last_update, captcha_passed) VALUES (?, ?, 1)", (user_id, int(time.time())))
        c.execute("UPDATE users SET captcha_passed = 1 WHERE user_id = ?", (user_id,))
        conn.commit()

    c.execute("SELECT captcha_passed, state, balance, lang, referrer_id FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    now = int(time.time())

    if not user:
        ref_id = 0
        if text.startswith("/start ") and text.split(" ")[1].isdigit():
            ref_id = int(text.split(" ")[1])
        c.execute("INSERT INTO users (user_id, last_update, referrer_id, captcha_passed) VALUES (?, ?, ?, ?)", (user_id, now, ref_id, 1 if is_admin else 0))
        conn.commit()
        user = (1 if is_admin else 0, 'idle', 0.0, 'ar', ref_id)

    captcha_passed, state, balance, lang, ref_id = user
    bal_float = float(balance or 0.0)
    current_min_withdraw = get_min_withdraw()

    # 1. التحقق من الكابتشا أولاً
    if captcha_passed == 0 and not is_admin:
        send_captcha(chat_id, lang)
        conn.close()
        return

    # 2. التحقق من القنوات الإجبارية
    if not is_admin:
        c.execute("SELECT url, ch_id FROM channels WHERE type = 'main'")
        for ch_url, ch_id in c.fetchall():
            if ch_id and not check_sub(user_id, ch_id):
                markup = {"inline_keyboard": [[{"text": "📢 Join / اشترك", "url": ch_url}], [{"text": "✅ Check / تحقق", "callback_data": "check_main_sub"}]]}
                send_msg(chat_id, get_text(lang, 'sub_req'), markup)
                conn.close()
                return

    system_btns = [get_text(lang, k) for k in ['btn_refresh', 'btn_withdraw', 'btn_team', 'btn_tasks', 'btn_speed_ch', 'btn_lang', 'btn_about', 'btn_stats', 'btn_calc', 'btn_support', 'btn_admin']]

    # 3. معالجة أزرار الكيبورد
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
        if current_bal < current_min_withdraw:
            send_msg(chat_id, get_text(lang, 'withdraw_err', min=current_min_withdraw))
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
        c.execute("SELECT id, description, url, reward FROM shortlinks")
        links = list(c.fetchall())
        if not links:
            send_msg(chat_id, "📋 لا توجد مهام روابط حالياً، انتظر تحديث الإدارة.")
        else:
            # ترتييب عشوائي فريد لكل مستخدم بناءً على الآيدي الخاص به
            rnd = random.Random(user_id)
            rnd.shuffle(links)
            
            send_msg(chat_id, "📋 <b>قائمة المهام المربحة (روابط مختصرة):</b>\nتخطى الرابط واجلب كلمة السر لتحصل على مكافأتك فوراً (كل مهمة تتجدد كل 24 ساعة):")
            for idx, l in enumerate(links, 1):
                task_id, desc, link_url, reward = l
                c.execute("SELECT claimed_at FROM claimed_tasks WHERE user_id = ? AND task_id = ?", (user_id, task_id))
                row_c = c.fetchone()
                if row_c and (now - row_c[0] < 86400):
                    status = "✅ تم إنجازها (تتجدد غداً)"
                    markup = None
                else:
                    status = f"المكافأة: <code>{reward:.8f}</code> DOGE"
                    markup = {"inline_keyboard": [
                        [{"text": f"🔗 فتح الرابط {idx}", "url": link_url}],
                        [{"text": f"🔑 إدخال كلمة سر المهمة {idx}", "callback_data": f"enter_pass_{task_id}"}]
                    ]}
                msg_body = f"📌 <b>مهمة رقم {idx}:</b> {desc}\n💰 {status}"
                send_msg(chat_id, msg_body, markup)
        conn.close()
        return

    elif text == get_text(lang, 'btn_speed_ch'):
        c.execute("SELECT id, name, url, ch_id FROM channels WHERE type = 'speed'")
        channels = c.fetchall()
        if not channels:
            send_msg(chat_id, "📢 لا توجد قنوات زيادة سرعة حالياً.")
        else:
            send_msg(chat_id, "⚡ <b>قنوات زيادة سرعة التعدين:</b>\nاشترك في أي قناة واضغط تحقق لتكسب +10% سرعة تعدين إضافية فورية لكل قناة!")
            for ch in channels:
                ch_id_pk, name, url, t_id = ch
                c.execute("SELECT ch_id FROM joined_speed_channels WHERE user_id = ? AND ch_id = ?", (user_id, ch_id_pk))
                if c.fetchone():
                    status_btn = [{"text": "✅ مفعلة (+10%)", "callback_data": "already_active"}]
                else:
                    status_btn = [
                        {"text": f"📢 اشترك في {name}", "url": url},
                        {"text": "⚡ تحقق وزد سرعتك", "callback_data": f"verify_speed_{ch_id_pk}"}
                    ]
                send_msg(chat_id, f"🔹 <b>{name}</b>", {"inline_keyboard": [status_btn]})
        conn.close()
        return

    elif text == get_text(lang, 'btn_calc'):
        send_msg(chat_id, get_text(lang, 'calc_text'))
        conn.close()
        return

    elif text == get_text(lang, 'btn_stats'):
        miners_dyn, eff_dyn = get_dynamic_stats()
        stats_msg = get_text(lang, 'stats_text', miners=miners_dyn, eff=eff_dyn)
        send_msg(chat_id, stats_msg)
        conn.close()
        return

    elif text == get_text(lang, 'btn_about'):
        send_msg(chat_id, get_text(lang, 'about_text'))
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

    # 4. معالجة الحالات النصية
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

        task_id = int(state.split('_')[2])
        c.execute("SELECT password, reward FROM shortlinks WHERE id = ?", (task_id,))
        link = c.fetchone()
        if link and text.strip() == link[0]:
            reward = float(link[1] or 0.0)
            c.execute("UPDATE users SET balance = balance + ?, state = 'idle' WHERE user_id = ?", (reward, user_id))
            c.execute("INSERT OR REPLACE INTO claimed_tasks (user_id, task_id, claimed_at) VALUES (?, ?, ?)", (user_id, task_id, now))
            conn.commit()
            send_msg(chat_id, f"🎉 <b>رائع جداً!</b> كلمة السر صحيحة.\nتمت إضافة <code>{reward:.8f}</code> DOGE إلى رصيدك.")
        else:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, "❌ <b>كلمة السر خاطئة!</b> تخطى الرابط واجلب الرمز من الصفحة الأخيرة.")
        conn.close()
        return

    elif state == 'admin_broadcast' and is_admin:
        if text in system_btns:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return
        c.execute("SELECT user_id FROM users")
        all_u = c.fetchall()
        for u in all_u:
            try:
                send_msg(u[0], f"📢 <b>إعلان رسمي من إدارة المنجم:</b>\n\n{text}")
            except Exception:
                pass
        c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
        conn.commit()
        send_msg(chat_id, f"✅ تم إرسال الإذاعة بنجاح إلى {len(all_u)} مستخدم.")
        conn.close()
        return

    elif state == 'admin_set_min_w' and is_admin:
        if text in system_btns:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return
        try:
            new_mw = float(text.strip())
            c.execute("UPDATE settings SET value = ? WHERE key = 'min_withdraw'", (str(new_mw),))
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, f"✅ تم تحديث الحد الأدنى للسحب بنجاح ليصبح: <code>{new_mw} DOGE</code>")
        except Exception:
            send_msg(chat_id, "❌ القيمة غير صالحة! أرسل رقماً عشرياً صحيحاً (مثال: 0.05)")
        conn.close()
        return

    elif state == 'admin_add_main_ch' and is_admin:
        if text in system_btns:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return

        target_ch_id = None
        target_title = "القناة الرسمية"
        target_link = ""

        if 'forward_from_chat' in msg:
            f_chat = msg['forward_from_chat']
            target_ch_id = str(f_chat['id'])
            target_title = f_chat.get('title', 'قناة رسمية')
            username = f_chat.get('username')
            if username:
                target_link = f"https://t.me/{username}"
            else:
                inv = call_api("exportChatInviteLink", {"chat_id": target_ch_id})
                if inv and inv.get('ok'):
                    target_link = inv['result']
                else:
                    target_link = f"https://t.me"
        else:
            cleaned = text.strip()
            if cleaned.startswith("https://t.me/"):
                target_link = cleaned
                u_part = cleaned.replace("https://t.me/", "").replace("/", "").replace("@", "")
                target_ch_id = "@" + u_part if not u_part.startswith("+") and not u_part.startswith("-") else u_part
            elif cleaned.startswith("@"):
                target_ch_id = cleaned
                target_link = f"https://t.me/{cleaned[1:]}"
            else:
                target_ch_id = cleaned
                target_link = f"https://t.me/{cleaned}"

        test = call_api("getChat", {"chat_id": target_ch_id})
        if test and test.get('ok'):
            target_title = test['result'].get('title', target_title)
            if not target_link or target_link == "https://t.me":
                inv = call_api("exportChatInviteLink", {"chat_id": target_ch_id})
                if inv and inv.get('ok'):
                    target_link = inv['result']
                else:
                    username = test['result'].get('username')
                    if username:
                        target_link = f"https://t.me/{username}"
                    else:
                        target_link = f"https://t.me"

            c.execute("INSERT INTO channels (name, url, ch_id, type) VALUES (?, ?, ?, 'main')", (target_title, target_link, str(target_ch_id)))
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, f"✅ <b>تمت إضافة القناة الإجبارية بنجاح!</b>\nالاسم: {target_title}\nالرابط: {target_link}\nالمعرف: <code>{target_ch_id}</code>")
        else:
            send_msg(chat_id, "❌ <b>فشل التحقق!</b>\nتأكد من رفع البوت كمشرف في القناة بكامل الصلاحيات ثم أعد توجيه أي رسالة منها هنا أو أرسل يوزرها الصحيح.")
        conn.close()
        return

    elif state == 'admin_add_speed_ch' and is_admin:
        if text in system_btns:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return

        target_ch_id = None
        target_title = "قناة سرعة"
        target_link = ""

        if 'forward_from_chat' in msg:
            f_chat = msg['forward_from_chat']
            target_ch_id = str(f_chat['id'])
            target_title = f_chat.get('title', 'قناة زيادة السرعة')
            username = f_chat.get('username')
            if username:
                target_link = f"https://t.me/{username}"
            else:
                inv = call_api("exportChatInviteLink", {"chat_id": target_ch_id})
                if inv and inv.get('ok'):
                    target_link = inv['result']
                else:
                    target_link = f"https://t.me"
        else:
            parts = text.split()
            if len(parts) >= 2:
                target_title = parts[0]
                cleaned = parts[1]
                if cleaned.startswith("https://t.me/"):
                    target_link = cleaned
                    u_part = cleaned.replace("https://t.me/", "").replace("/", "").replace("@", "")
                    target_ch_id = "@" + u_part if not u_part.startswith("+") and not u_part.startswith("-") else u_part
                else:
                    target_ch_id = cleaned if cleaned.startswith("@") else "@" + cleaned
                    target_link = f"https://t.me/{target_ch_id[1:]}"
            else:
                send_msg(chat_id, "❌ أرسل: الاسم والرابط\nأو قم بتوجيه رسالة مباشرة من القناة هنا بعد رفع البوت مشرفاً.")
                conn.close()
                return

        test = call_api("getChat", {"chat_id": target_ch_id})
        if test and test.get('ok'):
            target_title = test['result'].get('title', target_title)
            if not target_link or target_link == "https://t.me":
                inv = call_api("exportChatInviteLink", {"chat_id": target_ch_id})
                if inv and inv.get('ok'):
                    target_link = inv['result']
                else:
                    username = test['result'].get('username')
                    if username:
                        target_link = f"https://t.me/{username}"
                    else:
                        target_link = f"https://t.me"

            c.execute("INSERT INTO channels (name, url, ch_id, type) VALUES (?, ?, ?, 'speed')", (target_title, target_link, str(target_ch_id)))
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, f"✅ <b>تمت إضافة قناة زيادة السرعة بنجاح!</b>\nالاسم: {target_title}\nالرابط: {target_link}")
        else:
            send_msg(chat_id, "❌ البوت ليس مشرفاً في هذه القناة. ارفع البوت مشرفاً ثم وجه رسالة منها أو أرسل يوزرها الصحيح.")
        conn.close()
        return

    elif state == 'admin_add_shortlink' and is_admin:
        if text in system_btns:
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return
        try:
            parts = text.split('|')
            desc = parts[0].strip()
            url = parts[1].strip()
            pw = parts[2].strip()
            reward = float(parts[3].strip())
            c.execute("INSERT INTO shortlinks (description, url, password, reward) VALUES (?, ?, ?, ?)", (desc, url, pw, reward))
            c.execute("UPDATE users SET state = 'idle' WHERE user_id = ?", (user_id,))
            conn.commit()
            send_msg(chat_id, f"✅ <b>تمت إضافة مهمة الرابط بنجاح!</b>\nالوصف: {desc}\nالمكافأة: {reward:.8f} DOGE")
        except Exception:
            send_msg(chat_id, "❌ صيغة غير صحيحة! تأكد من استخدام العلامة | للفصل بين الحقول:\n<code>الوصف | الرابط | كلمة_السر | المكافأة</code>")
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

    if text == "/start":
        if not is_admin:
            c.execute("SELECT captcha_passed FROM users WHERE user_id = ?", (user_id,))
            row_cap = c.fetchone()
            if not row_cap or row_cap[0] == 0:
                send_captcha(chat_id, lang)
                conn.close()
                return

            c.execute("SELECT url, ch_id FROM channels WHERE type = 'main'")
            main_ch = c.fetchone()
            if main_ch and main_ch[1] and not check_sub(user_id, main_ch[1]):
                markup = {"inline_keyboard": [[{"text": "📢 Join / اشترك", "url": main_ch[0]}], [{"text": "✅ Check / تحقق", "callback_data": "check_main_sub"}]]}
                send_msg(chat_id, get_text(lang, 'sub_req'), markup)
                conn.close()
                return

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
    c.execute("SELECT lang, referrer_id, captcha_passed FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if not row:
        c.execute("INSERT OR IGNORE INTO users (user_id, last_update) VALUES (?, ?)", (user_id, int(time.time())))
        conn.commit()
        row = ('ar', 0, 0)

    lang, ref_id, cap_passed = row
    is_admin = c.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)).fetchone() is not None or user_id == OWNER_ID

    if data == "cap_ok":
        now = int(time.time())
        if cap_passed == 0 and ref_id and ref_id != 0:
            c.execute("UPDATE users SET speed = speed * 1.3, ref_count = ref_count + 1 WHERE user_id = ?", (ref_id,))
            ref_row = c.execute("SELECT lang FROM users WHERE user_id = ?", (ref_id,)).fetchone()
            if ref_row:
                send_msg(ref_id, get_text(ref_row[0], 'ref_notify'))

        c.execute("UPDATE users SET captcha_passed = 1 WHERE user_id = ?", (user_id,))
        conn.commit()

        delete_msg(chat_id, msg_id)
        
        c.execute("SELECT url, ch_id FROM channels WHERE type = 'main'")
        main_ch = c.fetchone()
        if main_ch and main_ch[1] and not check_sub(user_id, main_ch[1]):
            send_msg(chat_id, "✅ " + get_text(lang, 'captcha_ok'))
            markup = {"inline_keyboard": [[{"text": "📢 Join / اشترك", "url": main_ch[0]}], [{"text": "✅ Check / تحقق", "callback_data": "check_main_sub"}]]}
            send_msg(chat_id, get_text(lang, 'sub_req'), markup)
        else:
            send_msg(chat_id, "✅ " + get_text(lang, 'captcha_ok'), get_reply_keyboard(lang, is_admin))
            send_main_menu(chat_id, user_id, c, conn, lang)

    elif data == "cap_fail":
        delete_msg(chat_id, msg_id)
        send_msg(chat_id, get_text(lang, 'captcha_fail'))
        send_captcha(chat_id, lang)

    elif data == "check_main_sub":
        c.execute("SELECT url, ch_id FROM channels WHERE type = 'main'")
        main_ch = c.fetchone()
        if main_ch and main_ch[1] and check_sub(user_id, main_ch[1]):
            delete_msg(chat_id, msg_id)
            send_msg(chat_id, "✅ تم التحقق من اشتراكك بنجاح! مرحباً بك في المنجم.", get_reply_keyboard(lang, is_admin))
            send_main_menu(chat_id, user_id, c, conn, lang)
        else:
            call_api("answerCallbackQuery", {"callback_query_id": cq_id, "text": "❌ لم تشترك في القناة بعد! اشترك أولاً.", "show_alert": True})

    elif data.startswith("enter_pass_"):
        task_id = data.split("_")[2]
        c.execute("UPDATE users SET state = ? WHERE user_id = ?", (f"wait_pass_{task_id}", user_id))
        conn.commit()
        send_msg(chat_id, f"🔑 <b>أرسل الآن كلمة السر الخاصة بالمهمة رقم {task_id}:</b>")

    elif data.startswith("verify_speed_"):
        ch_id_pk = int(data.split("_")[2])
        c.execute("SELECT ch_id FROM channels WHERE id = ?", (ch_id_pk,))
        ch_row = c.fetchone()
        if ch_row and check_sub(user_id, ch_row[0]):
            c.execute("UPDATE users SET speed = speed * 1.1 WHERE user_id = ?", (user_id,))
            c.execute("INSERT OR IGNORE INTO joined_speed_channels (user_id, ch_id) VALUES (?, ?)", (user_id, ch_id_pk))
            conn.commit()
            send_msg(chat_id, "🎉 <b>مبروك!</b> تم التحقق من اشتراكك بنجاح وزادت سرعة تعدينك بنسبة <b>+10%</b>!")
        else:
            send_msg(chat_id, "❌ لم تشترك في القناة بعد! اشترك ثم اضغط زر التحقق مجدداً.")

    # ================= تفعيل أزرار الإدارة =================
    elif data == "admin_broadcast" and is_admin:
        c.execute("UPDATE users SET state = 'admin_broadcast' WHERE user_id = ?", (user_id,))
        conn.commit()
        send_msg(chat_id, "📢 <b>أرسل الآن الرسالة التي تريد إذاعتها لجميع مستخدمي البوت:</b>")

    elif data == "admin_set_min_w" and is_admin:
        c.execute("UPDATE users SET state = 'admin_set_min_w' WHERE user_id = ?", (user_id,))
        conn.commit()
        send_msg(chat_id, "⚙️ <b>تعديل الحد الأدنى للسحب:</b>\nأرسل القيمة الرقمية الجديدة بالـ DOGE (مثال: <code>0.02</code>):")

    elif data == "admin_top_refs" and is_admin:
        c.execute("SELECT user_id, ref_count, balance FROM users WHERE ref_count > 10 ORDER BY ref_count DESC LIMIT 30")
        top_list = c.fetchall()
        if not top_list:
            send_msg(chat_id, "👥 لا يوجد مستخدمين لديهم أكثر من 10 إحالات حالياً.")
        else:
            msg_top = "👥 <b>قائمة المستخدمين الأكثر دعوة (أكثر من 10 إحالات):</b>\n\n"
            for t in top_list:
                t_id, r_cnt, t_bal = t
                msg_top += f"👤 آيدي: <code>{t_id}</code>\n👥 الإحالات: <code>{r_cnt}</code>\n💰 الرصيد: <code>{t_bal:.4f} DOGE</code>\n-------------------\n"
            send_msg(chat_id, msg_top)

    elif data == "admin_add_main_ch" and is_admin:
        c.execute("UPDATE users SET state = 'admin_add_main_ch' WHERE user_id = ?", (user_id,))
        conn.commit()
        send_msg(chat_id, "➕ <b>إضافة قناة إجبارية:</b>\n\n1️⃣ ارفع البوت مشرفاً فيها أولاً.\n2️⃣ إذا كانت القناة خاصة: قم بـ <b>توجيه (Forward)</b> أي رسالة منها هنا مباشرة!\n3️⃣ إذا كانت عامة: أرسل يوزرها مثل <code>@channel</code> أو رابطها.")

    elif data == "admin_add_speed_ch" and is_admin:
        c.execute("UPDATE users SET state = 'admin_add_speed_ch' WHERE user_id = ?", (user_id,))
        conn.commit()
        send_msg(chat_id, "📢 <b>إضافة قناة لزيادة السرعة (+10%):</b>\n\n1️⃣ ارفع البوت مشرفاً فيها أولاً.\n2️⃣ إذا كانت خاصة: قم بـ <b>توجيه (Forward)</b> أي رسالة منها هنا مباشرة!\n3️⃣ إذا كانت عامة: أرسل يوزرها أو رابطها.")

    elif data == "admin_add_shortlink" and is_admin:
        c.execute("UPDATE users SET state = 'admin_add_shortlink' WHERE user_id = ?", (user_id,))
        conn.commit()
        send_msg(chat_id, "🔗 <b>إضافة مهمة رابط مختصر جديدة:</b>\nأرسل البيانات مفصولة بالعلامة | كالتالي:\n<code>الوصف | رابط_الموقع | كلمة_السر | المكافأة</code>\n\nمثال:\n<code>تخطى الرابط واجلب الكود | https://link.com/xxx | secret77 | 0.0002</code>")

    elif data == "admin_manage_channels" and is_admin:
        c.execute("SELECT id, name, type FROM channels")
        ch_list = c.fetchall()
        if not ch_list:
            send_msg(chat_id, "لا توجد قنوات مسجلة حالياً.")
        else:
            send_msg(chat_id, "🗑 <b>اضغط على القناة التي تريد حذفها فوراً:</b>")
            for ch in ch_list:
                ch_id_pk, name, c_type = ch
                t_label = "إجبارية" if c_type == 'main' else "سرعة"
                del_btn = {"inline_keyboard": [[{"text": f"❌ حذف: {name} ({t_label})", "callback_data": f"del_ch_{ch_id_pk}"}]]}
                send_msg(chat_id, f"📢 {name}", del_btn)

    elif data.startswith("del_ch_") and is_admin:
        del_pk = int(data.split("_")[2])
        c.execute("DELETE FROM channels WHERE id = ?", (del_pk,))
        conn.commit()
        send_msg(chat_id, "✅ تم حذف القناة من النظام بنجاح.")

    elif data == "admin_manage_tasks" and is_admin:
        c.execute("SELECT id, description FROM shortlinks")
        t_list = c.fetchall()
        if not t_list:
            send_msg(chat_id, "لا توجد مهام روابط مسجلة حالياً.")
        else:
            send_msg(chat_id, "🗑 <b>اضغط على المهمة التي تريد حذفها فوراً:</b>")
            for t in t_list:
                t_pk, desc = t
                del_btn = {"inline_keyboard": [[{"text": f"❌ حذف المهمة: {desc[:20]}...", "callback_data": f"del_task_{t_pk}"}]]}
                send_msg(chat_id, f"📌 {desc}", del_btn)

    elif data.startswith("del_task_") and is_admin:
        t_del_pk = int(data.split("_")[2])
        c.execute("DELETE FROM shortlinks WHERE id = ?", (t_del_pk,))
        conn.commit()
        send_msg(chat_id, "✅ تم حذف المهمة من النظام بنجاح.")

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

# ================= ممر Vercel Serverless =================
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
