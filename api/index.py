from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import time
import random
import re
import traceback
from supabase import create_client, Client

# ================= الإعدادات الأساسية وسحابية Supabase =================
TOKEN = "8960593021:AAFEn0HioVC4K2S_LkJWVgqJVMYYJt-xF4Q"
OWNER_ID = 6610111288
BOT_USERNAME = "Dogcoinibot"

SUPABASE_URL = "https://gaehidarrlvqbzxghjaw.supabase.co"
SUPABASE_KEY = "sb_publishable_EG_RTkeVr8L5oFiPDiY2jQ_9cpukYSW"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
        'main_menu': "⛏ <b>خوادم التعدين النشطة</b>\n\n💰 الرصيد المباشر: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ قوة التعدين: <code>{speed:.8f}</code> DOGE/يوم\n👥 أعضاء الفريق: <code>{refs}</code>\n\n<i>🟢 حالة الخادم: متصل ومستقر (سحابي).</i>",
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
        'main_menu': "⛏ <b>Active Mining Servers</b>\n\n💰 Live Balance: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ Hash Power: <code>{speed:.8f}</code> DOGE/Day\n👥 Team Size: <code>{refs}</code>\n\n<i>🟢 Server Status: Online & Stable (Cloud).</i>",
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

# ================= أدوات التعامل مع Supabase =================
def get_user(user_id):
    res = supabase.table("users").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None

def upsert_user(data):
    supabase.table("users").upsert(data).execute()

def update_user_fields(user_id, fields_dict):
    supabase.table("users").update(fields_dict).eq("user_id", user_id).execute()

def is_admin(user_id):
    if user_id == OWNER_ID:
        return True
    res = supabase.table("admins").select("*").eq("user_id", user_id).execute()
    return len(res.data) > 0

def get_min_withdraw():
    res = supabase.table("settings").select("value").eq("key", "min_withdraw").execute()
    if res.data:
        return float(res.data[0]['value'])
    return 0.01

def set_min_withdraw(val):
    supabase.table("settings").upsert({"key": "min_withdraw", "value": str(val)}).execute()

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
    total_growth = sum(random.Random(999 + d).randint(300, 450) for d in range(min(days_passed, 365)))
    miners = 16780 + total_growth
    random.seed(now_ts // 1800)
    eff = round(random.uniform(96.2, 98.7), 2)
    random.seed()
    return f"{miners:,}", eff

def get_reply_keyboard(lang, user_is_admin):
    kb = [
        [{"text": get_text(lang, 'btn_refresh')}],
        [{"text": get_text(lang, 'btn_withdraw')}, {"text": get_text(lang, 'btn_team')}],
        [{"text": get_text(lang, 'btn_tasks')}, {"text": get_text(lang, 'btn_speed_ch')}],
        [{"text": get_text(lang, 'btn_calc')}, {"text": get_text(lang, 'btn_stats')}],
        [{"text": get_text(lang, 'btn_about')}, {"text": get_text(lang, 'btn_support')}],
        [{"text": get_text(lang, 'btn_lang')}]
    ]
    if user_is_admin:
        kb.insert(0, [{"text": get_text(lang, 'btn_admin')}])
    return {"keyboard": kb, "resize_keyboard": True}

def send_captcha(chat_id, lang):
    btns = [{"text": "🔹", "callback_data": "cap_fail"} for _ in range(3)]
    btns.insert(random.randint(0, 3), {"text": "🔴", "callback_data": "cap_ok"})
    send_msg(chat_id, get_text(lang, 'captcha_msg'), {"inline_keyboard": [btns]})

def update_mining(user_id):
    user = get_user(user_id)
    if user:
        now = int(time.time())
        bal = float(user.get('balance') or 0.0)
        speed = float(user.get('speed') or 0.0000000115)
        last = int(user.get('last_update') or now)
        earned = (now - last) * speed
        update_user_fields(user_id, {"balance": bal + earned, "last_update": now})

def send_main_menu(chat_id, user_id, lang):
    update_mining(user_id)
    user = get_user(user_id)
    bal = float(user.get('balance') or 0.0)
    speed = float(user.get('speed') or 0.0000000115)
    refs = int(user.get('ref_count') or 0)
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

    user_is_admin = is_admin(user_id)
    now = int(time.time())

    user = get_user(user_id)
    if not user:
        ref_id = 0
        if text.startswith("/start ") and text.split(" ")[1].isdigit():
            ref_id = int(text.split(" ")[1])
        user = {
            "user_id": user_id,
            "balance": 0.0,
            "speed": 0.0000000115,
            "last_update": now,
            "captcha_passed": 1 if user_is_admin else 0,
            "referrer_id": ref_id,
            "ref_count": 0,
            "state": "idle",
            "lang": "ar"
        }
        upsert_user(user)
    elif user_is_admin and user.get('captcha_passed') == 0:
        update_user_fields(user_id, {"captcha_passed": 1})
        user['captcha_passed'] = 1

    captcha_passed = user.get('captcha_passed', 0)
    state = user.get('state', 'idle')
    balance = float(user.get('balance', 0.0))
    lang = user.get('lang', 'ar')

    if captcha_passed == 0 and not user_is_admin:
        send_captcha(chat_id, lang)
        return

    if not user_is_admin:
        ch_res = supabase.table("channels").select("*").eq("type", "main").execute()
        for ch in ch_res.data:
            if ch.get('ch_id') and not check_sub(user_id, ch['ch_id']):
                markup = {"inline_keyboard": [[{"text": "📢 Join / اشترك", "url": ch['url']}], [{"text": "✅ Check / تحقق", "callback_data": "check_main_sub"}]]}
                send_msg(chat_id, get_text(lang, 'sub_req'), markup)
                return

    system_btns = [get_text(lang, k) for k in ['btn_refresh', 'btn_withdraw', 'btn_team', 'btn_tasks', 'btn_speed_ch', 'btn_lang', 'btn_about', 'btn_stats', 'btn_calc', 'btn_support', 'btn_admin']]

    if text == get_text(lang, 'btn_refresh'):
        send_main_menu(chat_id, user_id, lang)
        return

    elif text == get_text(lang, 'btn_lang'):
        new_lang = 'en' if lang == 'ar' else 'ar'
        update_user_fields(user_id, {"lang": new_lang})
        send_msg(chat_id, "🌐 تم تغيير اللغة / Language Updated", get_reply_keyboard(new_lang, user_is_admin))
        send_main_menu(chat_id, user_id, new_lang)
        return

    elif text == get_text(lang, 'btn_withdraw'):
        update_mining(user_id)
        current_user = get_user(user_id)
        current_bal = float(current_user.get('balance', 0.0))
        current_min_withdraw = get_min_withdraw()
        if current_bal < current_min_withdraw:
            send_msg(chat_id, get_text(lang, 'withdraw_err', min=current_min_withdraw))
        else:
            update_user_fields(user_id, {"state": "wait_wallet"})
            send_msg(chat_id, get_text(lang, 'withdraw_req'))
        return

    elif text == get_text(lang, 'btn_team'):
        refs = int(user.get('ref_count', 0))
        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        send_msg(chat_id, get_text(lang, 'team_msg', refs=refs, link=link))
        return

    elif text == get_text(lang, 'btn_tasks'):
        t_res = supabase.table("shortlinks").select("*").execute()
        links = t_res.data
        if not links:
            send_msg(chat_id, "📋 لا توجد مهام روابط حالياً، انتظر تحديث الإدارة.")
        else:
            rnd = random.Random(user_id)
            rnd.shuffle(links)
            send_msg(chat_id, "📋 <b>قائمة المهام المربحة (روابط مختصرة):</b>\nتخطى الرابط واجلب كلمة السر لتحصل على مكافأتك فوراً (كل مهمة تتجدد كل 24 ساعة لكل مستخدم على حدة):")
            for l in links:
                task_id = l['id']
                desc = l['description']
                link_url = l['url']
                reward = l['reward']
                
                c_res = supabase.table("claimed_tasks").select("claimed_at").eq("user_id", user_id).eq("task_id", task_id).execute()
                claimed_row = c_res.data[0] if c_res.data else None
                
                if claimed_row and (now - claimed_row['claimed_at'] < 86400):
                    status = "✅ تم إنجازها (تتجدد غداً)"
                    markup = None
                else:
                    status = f"المكافأة: <code>{reward:.8f}</code> DOGE"
                    markup = {"inline_keyboard": [
                        [{"text": "🔗 فتح الرابط", "url": link_url}],
                        [{"text": "🔑 إدخال كلمة سر المهمة", "callback_data": f"enter_pass_{task_id}"}]
                    ]}
                msg_body = f"📌 <b>{desc}</b>\n💰 {status}"
                send_msg(chat_id, msg_body, markup)
        return

    elif text == get_text(lang, 'btn_speed_ch'):
        ch_res = supabase.table("channels").select("*").eq("type", "speed").execute()
        channels = ch_res.data
        if not channels:
            send_msg(chat_id, "📢 لا توجد قنوات زيادة سرعة حالياً.")
        else:
            send_msg(chat_id, "⚡ <b>قنوات زيادة سرعة التعدين:</b>\nاشترك في أي قناة واضغط تحقق لتكسب +10% سرعة تعدين إضافية فورية لكل قناة!")
            for ch in channels:
                ch_id_pk = ch['id']
                name = ch['name']
                url = ch['url']
                
                j_res = supabase.table("joined_speed_channels").select("*").eq("user_id", user_id).eq("ch_id", ch_id_pk).execute()
                if j_res.data:
                    status_btn = [{"text": "✅ مفعلة (+10%)", "callback_data": "already_active"}]
                else:
                    status_btn = [
                        {"text": f"📢 اشترك في {name}", "url": url},
                        {"text": "⚡ تحقق وزد سرعتك", "callback_data": f"verify_speed_{ch_id_pk}"}
                    ]
                send_msg(chat_id, f"🔹 <b>{name}</b>", {"inline_keyboard": [status_btn]})
        return

    elif text == get_text(lang, 'btn_calc'):
        send_msg(chat_id, get_text(lang, 'calc_text'))
        return

    elif text == get_text(lang, 'btn_stats'):
        miners_dyn, eff_dyn = get_dynamic_stats()
        stats_msg = get_text(lang, 'stats_text', miners=miners_dyn, eff=eff_dyn)
        send_msg(chat_id, stats_msg)
        return

    elif text == get_text(lang, 'btn_about'):
        send_msg(chat_id, get_text(lang, 'about_text'))
        return

    elif text == get_text(lang, 'btn_support'):
        send_msg(chat_id, get_text(lang, 'support_text'))
        return

    elif text == get_text(lang, 'btn_admin') and user_is_admin:
        send_admin_panel(chat_id, lang)
        return

    if state == 'wait_wallet':
        if text in system_btns:
            update_user_fields(user_id, {"state": "idle"})
            return

        admin_res = supabase.table("admins").select("user_id").execute()
        for adm in admin_res.data:
            send_msg(adm['user_id'], f"🔔 <b>طلب سحب عاجل!</b>\n👤 آيدي: <code>{user_id}</code>\n💰 الرصيد: <code>{balance:.8f}</code> DOGE\n🏦 المحفظة:\n<code>{text}</code>")

        # حفظ طلب السحب في السحابة
        supabase.table("withdrawals").insert({
            "user_id": user_id,
            "amount": balance,
            "wallet": text,
            "status": "pending",
            "created_at": now
        }).execute()

        update_user_fields(user_id, {"balance": 0.0, "state": "idle"})
        send_msg(chat_id, get_text(lang, 'withdraw_done'))
        return

    elif state.startswith('wait_pass_'):
        if text in system_btns:
            update_user_fields(user_id, {"state": "idle"})
            return

        task_id = int(state.split('_')[2])
        t_res = supabase.table("shortlinks").select("*").eq("id", task_id).execute()
        link_data = t_res.data[0] if t_res.data else None
        
        if link_data and text.strip() == link_data['password']:
            reward = float(link_data['reward'] or 0.0)
            new_bal = balance + reward
            update_user_fields(user_id, {"balance": new_bal, "state": "idle"})
            
            supabase.table("claimed_tasks").upsert({
                "user_id": user_id,
                "task_id": task_id,
                "claimed_at": now
            }).execute()
            
            send_msg(chat_id, f"🎉 <b>رائع جداً!</b> كلمة السر صحيحة.\nتمت إضافة <code>{reward:.8f}</code> DOGE إلى رصيدك.")
        else:
            update_user_fields(user_id, {"state": "idle"})
            send_msg(chat_id, "❌ <b>كلمة السر خاطئة!</b> تخطى الرابط واجلب الرمز من الصفحة الأخيرة.")
        return

    elif state == 'admin_broadcast' and user_is_admin:
        if text in system_btns:
            update_user_fields(user_id, {"state": "idle"})
            return
        all_u = supabase.table("users").select("user_id").execute().data
        for u in all_u:
            try:
                send_msg(u['user_id'], f"📢 <b>إعلان رسمي من إدارة المنجم:</b>\n\n{text}")
            except Exception:
                pass
        update_user_fields(user_id, {"state": "idle"})
        send_msg(chat_id, f"✅ تم إرسال الإذاعة بنجاح إلى {len(all_u)} مستخدم.")
        return

    elif state == 'admin_set_min_w' and user_is_admin:
        if text in system_btns:
            update_user_fields(user_id, {"state": "idle"})
            return
        try:
            new_mw = float(text.strip())
            set_min_withdraw(new_mw)
            update_user_fields(user_id, {"state": "idle"})
            send_msg(chat_id, f"✅ تم تحديث الحد الأدنى للسحب بنجاح ليصبح: <code>{new_mw} DOGE</code>")
        except Exception:
            send_msg(chat_id, "❌ القيمة غير صالحة! أرسل رقماً عشرياً صحيحاً (مثال: 0.02)")
        return

    elif state == 'admin_add_main_ch' and user_is_admin:
        if text in system_btns:
            update_user_fields(user_id, {"state": "idle"})
            return

        target_ch_id, target_title, target_link = None, "القناة الرسمية", ""
        if 'forward_from_chat' in msg:
            f_chat = msg['forward_from_chat']
            target_ch_id = str(f_chat['id'])
            target_title = f_chat.get('title', 'قناة رسمية')
            username = f_chat.get('username')
            target_link = f"https://t.me/{username}" if username else (call_api("exportChatInviteLink", {"chat_id": target_ch_id}).get('result') or "https://t.me")
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
            supabase.table("channels").insert({"name": target_title, "url": target_link, "ch_id": str(target_ch_id), "type": "main"}).execute()
            update_user_fields(user_id, {"state": "idle"})
            send_msg(chat_id, f"✅ <b>تمت إضافة القناة الإجبارية بنجاح!</b>\nالاسم: {target_title}\nالرابط: {target_link}")
        else:
            send_msg(chat_id, "❌ فشل التحقق! تأكد من رفع البوت مشرفاً فيها.")
        return

    elif state == 'admin_add_speed_ch' and user_is_admin:
        if text in system_btns:
            update_user_fields(user_id, {"state": "idle"})
            return

        target_ch_id, target_title, target_link = None, "قناة سرعة", ""
        if 'forward_from_chat' in msg:
            f_chat = msg['forward_from_chat']
            target_ch_id = str(f_chat['id'])
            target_title = f_chat.get('title', 'قناة زيادة السرعة')
            username = f_chat.get('username')
            target_link = f"https://t.me/{username}" if username else (call_api("exportChatInviteLink", {"chat_id": target_ch_id}).get('result') or "https://t.me")
        else:
            parts = text.split()
            if len(parts) >= 2:
                target_title = parts[0]
                cleaned = parts[1]
                target_ch_id = cleaned if cleaned.startswith("@") else "@" + cleaned
                target_link = f"https://t.me/{target_ch_id[1:]}"
            else:
                send_msg(chat_id, "❌ أرسل: الاسم والرابط أو قم بتوجيه رسالة.")
                return

        test = call_api("getChat", {"chat_id": target_ch_id})
        if test and test.get('ok'):
            target_title = test['result'].get('title', target_title)
            supabase.table("channels").insert({"name": target_title, "url": target_link, "ch_id": str(target_ch_id), "type": "speed"}).execute()
            update_user_fields(user_id, {"state": "idle"})
            send_msg(chat_id, f"✅ <b>تمت إضافة قناة زيادة السرعة بنجاح!</b>\nالاسم: {target_title}")
        else:
            send_msg(chat_id, "❌ البوت ليس مشرفاً في هذه القناة.")
        return

    elif state == 'admin_add_shortlink' and user_is_admin:
        if text in system_btns:
            update_user_fields(user_id, {"state": "idle"})
            return
        try:
            parts = text.split('|')
            desc = parts[0].strip()
            url = parts[1].strip()
            pw = parts[2].strip()
            reward = float(parts[3].strip())
            supabase.table("shortlinks").insert({"description": desc, "url": url, "password": pw, "reward": reward}).execute()
            update_user_fields(user_id, {"state": "idle"})
            send_msg(chat_id, f"✅ <b>تمت إضافة مهمة الرابط بنجاح!</b>\nالوصف: {desc}")
        except Exception:
            send_msg(chat_id, "❌ صيغة غير صحيحة! استخدم: <code>الوصف | الرابط | كلمة_السر | المكافأة</code>")
        return

    elif state == 'admin_wait_bal_id' and user_is_admin:
        if text in system_btns:
            update_user_fields(user_id, {"state": "idle"})
            return
        try:
            target_id = int(text)
            update_user_fields(user_id, {"state": f'admin_wait_bal_amt_{target_id}'})
            send_msg(chat_id, f"✅ تم تحديد المستخدم: <code>{target_id}</code>\nأرسل الآن المبلغ المراد إضافته:")
        except Exception:
            send_msg(chat_id, "❌ الآيدي غير صحيح.")
        return

    elif state.startswith('admin_wait_bal_amt_') and user_is_admin:
        if text in system_btns:
            update_user_fields(user_id, {"state": "idle"})
            return
        target_id = int(state.split('_')[4])
        try:
            amount = float(text)
            t_user = get_user(target_id)
            if t_user:
                new_b = float(t_user.get('balance', 0.0)) + amount
                update_user_fields(target_id, {"balance": new_b})
            update_user_fields(user_id, {"state": "idle"})
            send_msg(chat_id, f"✅ تمت إضافة {amount:.8f} DOGE للمستخدم بنجاح.")
            send_msg(target_id, f"🎉 <b>إهداء من الإدارة!</b>\nتمت إضافة <code>{amount:.8f}</code> DOGE إلى رصيدك.")
        except Exception:
            send_msg(chat_id, "❌ المبلغ غير صحيح.")
        return

    elif state == 'admin_wait_admin_id' and user_id == OWNER_ID:
        try:
            new_admin_id = int(text)
            supabase.table("admins").upsert({"user_id": new_admin_id}).execute()
            update_user_fields(user_id, {"state": "idle"})
            send_msg(chat_id, f"✅ تم تعيين المستخدم <code>{new_admin_id}</code> كمشرف بنجاح.")
        except Exception:
            send_msg(chat_id, "❌ الآيدي غير صحيح.")
        return

    if text == "/start":
        if not user_is_admin:
            if user.get('captcha_passed', 0) == 0:
                send_captcha(chat_id, lang)
                return
            ch_res = supabase.table("channels").select("*").eq("type", "main").execute()
            for ch in ch_res.data:
                if ch.get('ch_id') and not check_sub(user_id, ch['ch_id']):
                    markup = {"inline_keyboard": [[{"text": "📢 Join / اشترك", "url": ch['url']}], [{"text": "✅ Check / تحقق", "callback_data": "check_main_sub"}]]}
                    send_msg(chat_id, get_text(lang, 'sub_req'), markup)
                    return

        send_msg(chat_id, "✅", get_reply_keyboard(lang, user_is_admin))
        send_main_menu(chat_id, user_id, lang)

    elif text == "/admin" and user_is_admin:
        send_admin_panel(chat_id, lang)

# ================= معالجة نقرات الأزرار =================
def process_callback(cq):
    chat_id = cq['message']['chat']['id']
    user_id = cq['from']['id']
    data = cq.get('data', '')
    msg_id = cq['message']['message_id']
    cq_id = cq['id']

    call_api("answerCallbackQuery", {"callback_query_id": cq_id})

    user = get_user(user_id)
    if not user:
        user = {"user_id": user_id, "last_update": int(time.time())}
        upsert_user(user)

    lang = user.get('lang', 'ar')
    ref_id = user.get('referrer_id', 0)
    cap_passed = user.get('captcha_passed', 0)
    user_is_admin = is_admin(user_id)

    if data == "cap_ok":
        now = int(time.time())
        if cap_passed == 0 and ref_id and ref_id != 0:
            ref_user = get_user(ref_id)
            if ref_user:
                new_speed = float(ref_user.get('speed', 0.0000000115)) * 1.3
                new_refs = int(ref_user.get('ref_count', 0)) + 1
                update_user_fields(ref_id, {"speed": new_speed, "ref_count": new_refs})
                send_msg(ref_id, get_text(ref_user.get('lang', 'ar'), 'ref_notify'))

        update_user_fields(user_id, {"captcha_passed": 1})
        delete_msg(chat_id, msg_id)

        ch_res = supabase.table("channels").select("*").eq("type", "main").execute()
        main_ch = ch_res.data[0] if ch_res.data else None
        if main_ch and main_ch.get('ch_id') and not check_sub(user_id, main_ch['ch_id']):
            send_msg(chat_id, "✅ " + get_text(lang, 'captcha_ok'))
            markup = {"inline_keyboard": [[{"text": "📢 Join / اشترك", "url": main_ch['url']}], [{"text": "✅ Check / تحقق", "callback_data": "check_main_sub"}]]}
            send_msg(chat_id, get_text(lang, 'sub_req'), markup)
        else:
            send_msg(chat_id, "✅ " + get_text(lang, 'captcha_ok'), get_reply_keyboard(lang, user_is_admin))
            send_main_menu(chat_id, user_id, lang)

    elif data == "cap_fail":
        delete_msg(chat_id, msg_id)
        send_msg(chat_id, get_text(lang, 'captcha_fail'))
        send_captcha(chat_id, lang)

    elif data == "check_main_sub":
        ch_res = supabase.table("channels").select("*").eq("type", "main").execute()
        main_ch = ch_res.data[0] if ch_res.data else None
        if main_ch and main_ch.get('ch_id') and check_sub(user_id, main_ch['ch_id']):
            delete_msg(chat_id, msg_id)
            send_msg(chat_id, "✅ تم التحقق من اشتراكك بنجاح! مرحباً بك في المنجم.", get_reply_keyboard(lang, user_is_admin))
            send_main_menu(chat_id, user_id, lang)
        else:
            call_api("answerCallbackQuery", {"callback_query_id": cq_id, "text": "❌ لم تشترك في القناة بعد! اشترك أولاً.", "show_alert": True})

    elif data.startswith("enter_pass_"):
        task_id = data.split("_")[2]
        update_user_fields(user_id, {"state": f"wait_pass_{task_id}"})
        send_msg(chat_id, f"🔑 <b>أرسل الآن كلمة السر الخاصة بالمهمة:</b>")

    elif data.startswith("verify_speed_"):
        ch_id_pk = int(data.split("_")[2])
        ch_row = supabase.table("channels").select("*").eq("id", ch_id_pk).execute().data
        if ch_row and check_sub(user_id, ch_row[0]['ch_id']):
            curr_speed = float(user.get('speed', 0.0000000115))
            update_user_fields(user_id, {"speed": curr_speed * 1.1})
            supabase.table("joined_speed_channels").upsert({"user_id": user_id, "ch_id": ch_id_pk}).execute()
            send_msg(chat_id, "🎉 <b>مبروك!</b> تم التحقق من اشتراكك بنجاح وزادت سرعة تعدينك بنسبة <b>+10%</b>!")
        else:
            send_msg(chat_id, "❌ لم تشترك في القناة بعد! اشترك ثم اضغط زر التحقق مجدداً.")

    elif data == "admin_broadcast" and user_is_admin:
        update_user_fields(user_id, {"state": "admin_broadcast"})
        send_msg(chat_id, "📢 <b>أرسل الآن الرسالة التي تريد إذاعتها لجميع مستخدمي البوت:</b>")

    elif data == "admin_set_min_w" and user_is_admin:
        update_user_fields(user_id, {"state": "admin_set_min_w"})
        send_msg(chat_id, "⚙️ <b>تعديل الحد الأدنى للسحب:</b>\nأرسل القيمة الرقمية الجديدة بالـ DOGE (مثال: <code>0.02</code>):")

    elif data == "admin_top_refs" and user_is_admin:
        top_list = supabase.table("users").select("*").gt("ref_count", 10).order("ref_count", desc=True).limit(30).execute().data
        if not top_list:
            send_msg(chat_id, "👥 لا يوجد مستخدمين لديهم أكثر من 10 إحالات حالياً.")
        else:
            msg_top = "👥 <b>قائمة المستخدمين الأكثر دعوة (أكثر من 10 إحالات):</b>\n\n"
            for t in top_list:
                msg_top += f"👤 آيدي: <code>{t['user_id']}</code>\n👥 الإحالات: <code>{t['ref_count']}</code>\n💰 الرصيد: <code>{float(t['balance']):.4f} DOGE</code>\n-------------------\n"
            send_msg(chat_id, msg_top)

    elif data == "admin_add_main_ch" and user_is_admin:
        update_user_fields(user_id, {"state": "admin_add_main_ch"})
        send_msg(chat_id, "➕ <b>إضافة قناة إجبارية:</b>\n\n1️⃣ ارفع البوت مشرفاً فيها أولاً.\n2️⃣ قم بـ <b>توجيه (Forward)</b> أي رسالة منها هنا مباشرة أو أرسل يوزرها مثل <code>@channel</code>.")

    elif data == "admin_add_speed_ch" and user_is_admin:
        update_user_fields(user_id, {"state": "admin_add_speed_ch"})
        send_msg(chat_id, "📢 <b>إضافة قناة لزيادة السرعة (+10%):</b>\n\n1️⃣ ارفع البوت مشرفاً فيها أولاً.\n2️⃣ قم بـ <b>توجيه (Forward)</b> أي رسالة منها هنا مباشرة أو أرسل يوزرها.")

    elif data == "admin_add_shortlink" and user_is_admin:
        update_user_fields(user_id, {"state": "admin_add_shortlink"})
        send_msg(chat_id, "🔗 <b>إضافة مهمة رابط مختصر جديدة:</b>\nاستخدم: <code>الوصف | الرابط | كلمة_السر | المكافأة</code>")

    elif data == "admin_manage_channels" and user_is_admin:
        ch_list = supabase.table("channels").select("*").execute().data
        if not ch_list:
            send_msg(chat_id, "لا توجد قنوات مسجلة حالياً.")
        else:
            send_msg(chat_id, "🗑 <b>اضغط على القناة التي تريد حذفها فوراً:</b>")
            for ch in ch_list:
                t_label = "إجبارية" if ch['type'] == 'main' else "سرعة"
                del_btn = {"inline_keyboard": [[{"text": f"❌ حذف: {ch['name']} ({t_label})", "callback_data": f"del_ch_{ch['id']}"}]]}
                send_msg(chat_id, f"📢 {ch['name']}", del_btn)

    elif data.startswith("del_ch_") and user_is_admin:
        del_pk = int(data.split("_")[2])
        supabase.table("channels").delete().eq("id", del_pk).execute()
        send_msg(chat_id, "✅ تم حذف القناة من النظام بنجاح.")

    elif data == "admin_manage_tasks" and user_is_admin:
        t_list = supabase.table("shortlinks").select("*").execute().data
        if not t_list:
            send_msg(chat_id, "لا توجد مهام روابط مسجلة حالياً.")
        else:
            send_msg(chat_id, "🗑 <b>اضغط على المهمة التي تريد حذفها فوراً:</b>")
            for t in t_list:
                del_btn = {"inline_keyboard": [[{"text": f"❌ حذف: {t['description'][:20]}...", "callback_data": f"del_task_{t['id']}"}]]}
                send_msg(chat_id, f"📌 {t['description']}", del_btn)

    elif data.startswith("del_task_") and user_is_admin:
        t_del_pk = int(data.split("_")[2])
        supabase.table("shortlinks").delete().eq("id", t_del_pk).execute()
        send_msg(chat_id, "✅ تم حذف المهمة من النظام بنجاح.")

    elif data == "admin_add_bal" and user_is_admin:
        update_user_fields(user_id, {"state": "admin_wait_bal_id"})
        send_msg(chat_id, "💰 أرسل <b>الآيدي (ID)</b> الخاص بالمستخدم:")

    elif data == "admin_add_admin" and user_id == OWNER_ID:
        update_user_fields(user_id, {"state": "admin_wait_admin_id"})
        send_msg(chat_id, "👑 أرسل <b>الآيدي (ID)</b> الخاص بالمشرف الجديد:")

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
