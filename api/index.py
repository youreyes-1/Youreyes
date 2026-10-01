from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import time
import random
import traceback
from supabase import create_client, Client

# ================= الإعدادات الأساسية =================
TOKEN = "8960593021:AAFEn0HioVC4K2S_LkJWVgqJVMYYJt-xF4Q"
OWNER_ID = 6610111288
BOT_USERNAME = "Dogcoinibot"

SUPABASE_URL = "https://gaehidarrlvqbzxghjaw.supabase.co"
SUPABASE_KEY = "sb_publishable_EG_RTkeVr8L5oFiPDiY2jQ_9cpukYSW"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

LANG = {
    'en': {
        'btn_refresh': "🔄 Refresh Data",
        'btn_withdraw': "💸 Withdraw",
        'btn_team': "👥 Team (3 Tiers)",
        'btn_tasks': "🔗 Shortlinks Tasks",
        'btn_reward_ch': "🎁 Join & Earn",
        'btn_daily_bonus': "🎁 Daily Bonus",
        'btn_about': "🖥 Mining Hardware",
        'btn_stats': "📊 Network Stats",
        'btn_calc': "🧮 Profit Calculator",
        'btn_support': "📞 Support",
        'btn_lang': "🌐 العربية",
        'btn_admin': "👑 Admin Panel",
        'captcha_msg': "🤖 <b>Anti-Bot System:</b>\nClick the unique symbol (🔴) to authenticate.",
        'captcha_ok': "Human verification successful!",
        'captcha_fail': "❌ Verification failed! Please try again.",
        'sub_req': "⚠ <b>Action Required!</b>\nJoin ALL our official channels below to unlock your miner:",
        'main_menu': "⛏ <b>Active Mining Servers</b>\n\n💰 Live Balance: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ Hash Power: <code>{speed:.8f}</code> DOGE/Day\n👥 Direct Team: <code>{refs}</code>\n\n<i>🟢 Server Status: Online & Stable (Cloud).</i>",
        'team_msg': "👥 <b>Multi-Tier Partner Program:</b>\nBuild your network and earn from 3 levels deep!\n\n🥇 Tier 1 (Direct): <b>+{t1}%</b> speed\n🥈 Tier 2: <b>+{t2}%</b> speed\n🥉 Tier 3: <b>+{t3}%</b> speed\n\n📊 Direct Invites: <code>{refs}</code>\n🔗 Your Referral Link:\n<code>{link}</code>",
        'withdraw_err': "❌ Balance is below the minimum threshold ({min} DOGE).",
        'withdraw_req': "💸 <b>Secure Withdrawal:</b>\nSend your <b>Dogecoin (FaucetPay)</b> wallet address (Start with D or Email):",
        'withdraw_done': "✅ <b>Request Logged!</b>\nYour payout is under review.",
        'ref_notify': "🎉 <b>Great News!</b>\nA user joined your network (Tier {level}). Speed increased by {ref_p}%!",
        'calc_text': "🧮 <b>Profit Calculator:</b>\n• 10-15 Referrals = Massive Boost.\n• 30-40 Referrals = <b>$5 to $8 USD daily</b> in DOGE!\n<i>Share your link to maximize income.</i>",
        'about_text': "🖥️ <b>Hardware Infrastructure:</b>\nPowered by massive arrays of <b>NVIDIA RTX 4090</b> rigs paired with high-efficiency <b>Antminer L7</b> units operating Scrypt algorithms under liquid cooling.",
        'stats_text': "📊 <b>Live Network Stats:</b>\n👤 Active Miners: <code>{miners}</code>\n⚡ Hashrate: <code>9.2 GH/s Scrypt</code>\n💸 Paid Today: <code>1,450 DOGE</code>\n🟢 Rig Uptime: <code>{eff}%</code>",
        'support_text': "📞 <b>Customer Support:</b>\nResponse time is currently 24-48 hours.",
        'admin_panel': "👑 <b>Command Center:</b>\nSelect an action:"
    },
    'ar': {
        'btn_refresh': "🔄 تحديث الأرباح",
        'btn_withdraw': "💸 سحب الرصيد",
        'btn_team': "👥 فريقك (3 أجيال)",
        'btn_tasks': "🔗 المهام والروابط",
        'btn_reward_ch': "🎁 اشترك واربح",
        'btn_daily_bonus': "🎁 الهدية اليومية",
        'btn_about': "🖥 عتاد التعدين",
        'btn_stats': "📊 إحصائيات المنجم",
        'btn_calc': "🧮 حاسبة الأرباح",
        'btn_support': "📞 الدعم الفني",
        'btn_lang': "🌐 English",
        'btn_admin': "👑 الإدارة (للمشرفين)",
        'captcha_msg': "🤖 <b>نظام الحماية (Anti-Bot):</b>\nاضغط على الرمز المختلف (🔴) للبدء.",
        'captcha_ok': "تم التحقق البشري بنجاح!",
        'captcha_fail': "❌ فشل التحقق الأمني! حاول مجدداً.",
        'sub_req': "⚠️ <b>شرط أساسي!</b>\nيجب عليك الاشتراك في جميع القنوات أدناه لتفعيل حسابك:",
        'main_menu': "⛏ <b>خوادم التعدين النشطة</b>\n\n💰 الرصيد المباشر: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ قوة التعدين: <code>{speed:.8f}</code> DOGE/يوم\n👥 إحالاتك المباشرة: <code>{refs}</code>\n\n<i>🟢 حالة الخادم: متصل ومستقر (سحابي).</i>",
        'team_msg': "👥 <b>نظام الإحالات الهرمي (3 أجيال):</b>\nابنِ شبكتك واربح من دعوات أصدقائك وأصدقاء أصدقائك!\n\n🥇 الجيل الأول (مباشر): <b>+{t1}%</b> سرعة\n🥈 الجيل الثاني: <b>+{t2}%</b> سرعة\n🥉 الجيل الثالث: <b>+{t3}%</b> سرعة\n\n📊 إحالاتك المباشرة: <code>{refs}</code> عضو\n🔗 رابط الدعوة الخاص بك:\n<code>{link}</code>",
        'withdraw_err': "❌ رصيدك الحالي أقل من الحد الأدنى للسحب ({min} DOGE).",
        'withdraw_req': "💸 <b>بوابة السحب الآمنة:</b>\nأرسل عنوان محفظة <b>Dogecoin (FaucetPay)</b> (يبدأ بحرف D أو الإيميل):",
        'withdraw_done': "✅ <b>تم استلام طلب السحب!</b>\nالطلب قيد المراجعة المالية.",
        'ref_notify': "🎉 <b>أخبار ممتازة!</b>\nانضم شخص لشبكتك (من الجيل {level}). زادت سرعتك بنسبة {ref_p}%!",
        'calc_text': "🧮 <b>حاسبة العوائد:</b>\n• 10-15 شخص = سرعة تتضاعف بقوة.\n• 30-40 شخص = <b>5$ إلى 8$ يومياً</b> تسحبها مباشرة!\n💡 انسخ رابطك وانشره.",
        'about_text': "🖥️ <b>البنية التحتية:</b>\nنعتمد على مصفوفات <b>NVIDIA RTX 4090</b> ووحدات <b>Antminer L7</b> لفك تشفير العملة بأعلى كفاءة.",
        'stats_text': "📊 <b>إحصائيات الشبكة:</b>\n👤 عمال التعدين: <code>{miners}</code>\n⚡ قوة الهاش: <code>9.2 GH/s Scrypt</code>\n💸 سحوبات اليوم: <code>1,450 DOGE</code>\n🟢 كفاءة التشغيل: <code>{eff}%</code>",
        'support_text': "📞 <b>مركز خدمة العملاء:</b>\nنظراً للضغط، يستغرق الرد من 24 إلى 48 ساعة.",
        'admin_panel': "👑 <b>مركز القيادة:</b>\nاختر العملية المطلوبة:"
    }
}

# ================= أدوات التخزين السحابي =================
def get_user(user_id):
    res = supabase.table("users").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None

def update_user(user_id, fields_dict):
    supabase.table("users").update(fields_dict).eq("user_id", user_id).execute()

def get_setting(key, default_val):
    res = supabase.table("settings").select("value").eq("key", key).execute()
    return res.data[0]['value'] if res.data else default_val

def set_setting(key, val):
    supabase.table("settings").upsert({"key": key, "value": str(val)}).execute()

def is_admin(user_id):
    if user_id == OWNER_ID: return True
    return len(supabase.table("admins").select("*").eq("user_id", user_id).execute().data) > 0

# ================= أدوات تيليجرام =================
def call_api(method, payload):
    api_url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    req = urllib.request.Request(api_url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try: return json.loads(urllib.request.urlopen(req, timeout=5).read().decode('utf-8'))
    except Exception: return None

def send_msg(chat_id, text, markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if markup: payload["reply_markup"] = markup
    return call_api("sendMessage", payload)

def delete_msg(chat_id, msg_id):
    return call_api("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})

def check_sub(user_id, channel_id):
    if not channel_id: return True
    res = call_api("getChatMember", {"chat_id": channel_id, "user_id": user_id})
    if res and res.get('ok'): return res['result']['status'] in ['member', 'administrator', 'creator']
    return False

def get_text(lang, key, **kwargs):
    text = LANG.get(lang, LANG['en']).get(key, "")
    return text.format(**kwargs) if kwargs else text

def get_dynamic_stats():
    now_ts = int(time.time())
    days_passed = max(0, (now_ts - 1788220800) // 86400)
    miners = 16780 + sum(random.Random(999 + d).randint(300, 450) for d in range(min(days_passed, 365)))
    random.seed(now_ts // 1800)
    eff = round(random.uniform(96.2, 98.7), 2)
    random.seed()
    return f"{miners:,}", eff

def get_reply_keyboard(lang, user_is_admin):
    kb = [
        [{"text": get_text(lang, 'btn_refresh')}],
        [{"text": get_text(lang, 'btn_withdraw')}, {"text": get_text(lang, 'btn_team')}],
        [{"text": get_text(lang, 'btn_tasks')}, {"text": get_text(lang, 'btn_reward_ch')}],
        [{"text": get_text(lang, 'btn_daily_bonus')}, {"text": get_text(lang, 'btn_calc')}],
        [{"text": get_text(lang, 'btn_stats')}, {"text": get_text(lang, 'btn_support')}],
        [{"text": get_text(lang, 'btn_about')}, {"text": get_text(lang, 'btn_lang')}]
    ]
    if user_is_admin: kb.insert(0, [{"text": get_text(lang, 'btn_admin')}])
    return {"keyboard": kb, "resize_keyboard": True}

# ================= التحديث المدمج =================
def calculate_and_update_mining(user):
    now = int(time.time())
    bal = float(user.get('balance', 0.0))
    speed = float(user.get('speed', 0.0000000115))
    last = int(user.get('last_update') or now)
    earned = (now - last) * speed
    if earned > 0:
        user['balance'] = bal + earned
        user['last_update'] = now
        update_user(user['user_id'], {"balance": user['balance'], "last_update": now})
    return user

# ================= معالجة الرسائل =================
def process_message(msg):
    chat_id = msg['chat']['id']
    user_id = msg['from']['id']
    text = msg.get('text', '')
    now = int(time.time())

    user_is_admin = is_admin(user_id)
    user = get_user(user_id)
    
    if not user:
        ref_id = int(text.split(" ")[1]) if text.startswith("/start ") and text.split(" ")[1].isdigit() else 0
        user = {"user_id": user_id, "balance": 0.0, "speed": 0.0000000115, "last_update": now, 
                "captcha_passed": 1 if user_is_admin else 0, "referrer_id": ref_id, "ref_count": 0, "state": "idle", "lang": "en"}
        supabase.table("users").upsert(user).execute()
    elif user_is_admin and user.get('captcha_passed') == 0:
        update_user(user_id, {"captcha_passed": 1})
        user['captcha_passed'] = 1

    lang = user.get('lang', 'en')
    state = user.get('state', 'idle')

    if user.get('captcha_passed', 0) == 0 and not user_is_admin:
        btns = [{"text": "🔹", "callback_data": "cap_fail"} for _ in range(3)]
        btns.insert(random.randint(0, 3), {"text": "🔴", "callback_data": "cap_ok"})
        send_msg(chat_id, get_text(lang, 'captcha_msg'), {"inline_keyboard": [btns]})
        return

    if not user_is_admin:
        main_channels = supabase.table("channels").select("*").eq("type", "main").execute().data
        unjoined = [ch for ch in main_channels if ch.get('ch_id') and not check_sub(user_id, ch['ch_id'])]
        if unjoined:
            markup = {"inline_keyboard": []}
            for ch in unjoined: markup["inline_keyboard"].append([{"text": f"📢 Join {ch['name']}", "url": ch['url']}])
            markup["inline_keyboard"].append([{"text": "✅ Verify / تحقق", "callback_data": "check_main_sub"}])
            send_msg(chat_id, get_text(lang, 'sub_req'), markup)
            return

    system_btns = [get_text(lang, k) for k in ['btn_refresh', 'btn_withdraw', 'btn_team', 'btn_tasks', 'btn_reward_ch', 'btn_daily_bonus', 'btn_lang', 'btn_about', 'btn_stats', 'btn_calc', 'btn_support', 'btn_admin']]

    if text == get_text(lang, 'btn_refresh') or text == "/start":
        user = calculate_and_update_mining(user)
        if text == "/start": send_msg(chat_id, "✅", get_reply_keyboard(lang, user_is_admin))
        send_msg(chat_id, get_text(lang, 'main_menu', balance=float(user['balance']), speed=float(user['speed'])*86400, refs=int(user['ref_count'])))
        return

    elif text == get_text(lang, 'btn_lang'):
        new_lang = 'ar' if lang == 'en' else 'en'
        update_user(user_id, {"lang": new_lang})
        send_msg(chat_id, "🌐 تم تغيير اللغة / Language Updated", get_reply_keyboard(new_lang, user_is_admin))
        user = calculate_and_update_mining(user)
        send_msg(chat_id, get_text(new_lang, 'main_menu', balance=float(user['balance']), speed=float(user['speed'])*86400, refs=int(user['ref_count'])))
        return

    elif text == get_text(lang, 'btn_withdraw'):
        user = calculate_and_update_mining(user)
        min_w = float(get_setting("min_withdraw", "0.01"))
        if float(user['balance']) < min_w:
            send_msg(chat_id, get_text(lang, 'withdraw_err', min=min_w))
        else:
            update_user(user_id, {"state": "wait_wallet"})
            send_msg(chat_id, get_text(lang, 'withdraw_req'))
        return

    elif text == get_text(lang, 'btn_team'):
        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        t1 = get_setting("ref_t1", "50")
        t2 = get_setting("ref_t2", "20")
        t3 = get_setting("ref_t3", "5")
        send_msg(chat_id, get_text(lang, 'team_msg', t1=t1, t2=t2, t3=t3, refs=int(user['ref_count']), link=link))
        return

    elif text == get_text(lang, 'btn_daily_bonus'):
        c_res = supabase.table("claimed_tasks").select("claimed_at").eq("user_id", user_id).eq("task_id", 0).execute()
        if c_res.data and (now - c_res.data[0]['claimed_at'] < 86400):
            rem = 86400 - (now - c_res.data[0]['claimed_at'])
            send_msg(chat_id, f"⏳ {'لقد حصلت على الهدية اليوم! عُد بعد' if lang=='ar' else 'Already claimed! Come back in'} {rem//3600}h {(rem%3600)//60}m.")
        else:
            daily_b = float(get_setting("daily_bonus", "0.005"))
            new_bal = float(user['balance']) + daily_b
            update_user(user_id, {"balance": new_bal})
            supabase.table("claimed_tasks").upsert({"user_id": user_id, "task_id": 0, "claimed_at": now}).execute()
            send_msg(chat_id, f"🎉 {'مبروك! حصلت على هديتك اليومية:' if lang=='ar' else 'You received your daily bonus:'} {daily_b} DOGE")
        return

    elif text == get_text(lang, 'btn_tasks'):
        links = supabase.table("shortlinks").select("*").execute().data
        if not links:
            send_msg(chat_id, "📋 لا توجد مهام حالياً." if lang=='ar' else "📋 No tasks available.")
            return
        random.Random(user_id).shuffle(links)
        send_msg(chat_id, "📋 <b>قائمة المهام المربحة:</b>" if lang=='ar' else "📋 <b>Shortlinks Tasks:</b>")
        for l in links:
            c_res = supabase.table("claimed_tasks").select("claimed_at").eq("user_id", user_id).eq("task_id", l['id']).execute()
            if c_res.data and (now - c_res.data[0]['claimed_at'] < 86400):
                markup = None
                status = "✅ منجزة (تتجدد غداً)" if lang=='ar' else "✅ Done (Renews tomorrow)"
            else:
                markup = {"inline_keyboard": [[{"text": "🔗 Open / فتح", "url": l['url']}], [{"text": "🔑 Enter Password / أدخل الرمز", "callback_data": f"enter_pass_{l['id']}"}]]}
                status = f"Reward: <code>{l['reward']:.8f}</code> DOGE"
            send_msg(chat_id, f"📌 <b>{l['description']}</b>\n💰 {status}", markup)
        return

    elif text == get_text(lang, 'btn_reward_ch'):
        channels = supabase.table("channels").select("*").eq("type", "speed").execute().data
        if not channels: return send_msg(chat_id, "📢 لا توجد قنوات مكافآت حالياً." if lang=='ar' else "📢 No reward channels available.")
        ch_reward_val = get_setting("ch_reward", "0.004")
        send_msg(chat_id, f"🎁 <b>اشترك واربح {ch_reward_val} DOGE فوراً:</b>" if lang=='ar' else f"🎁 <b>Join & Earn {ch_reward_val} DOGE:</b>")
        for ch in channels:
            j_res = supabase.table("joined_speed_channels").select("*").eq("user_id", user_id).eq("ch_id", ch['id']).execute()
            status_btn = [{"text": "✅ Claimed / تم الاستلام", "callback_data": "already_active"}] if j_res.data else [{"text": f"📢 Join {ch['name']}", "url": ch['url']}, {"text": "🎁 Verify & Claim", "callback_data": f"verify_reward_{ch['id']}"}]
            send_msg(chat_id, f"🔹 <b>{ch['name']}</b>", {"inline_keyboard": [status_btn]})
        return

    elif text == get_text(lang, 'btn_calc'): return send_msg(chat_id, get_text(lang, 'calc_text'))
    elif text == get_text(lang, 'btn_stats'): 
        miners_dyn, eff_dyn = get_dynamic_stats()
        return send_msg(chat_id, get_text(lang, 'stats_text', miners=miners_dyn, eff=eff_dyn))
    elif text == get_text(lang, 'btn_about'): return send_msg(chat_id, get_text(lang, 'about_text'))
    elif text == get_text(lang, 'btn_support'):
        custom_support = get_setting(f"support_text_{lang}", "")
        return send_msg(chat_id, custom_support if custom_support else get_text(lang, 'support_text'))
    
    elif text == get_text(lang, 'btn_admin') and user_is_admin:
        min_w = get_setting("min_withdraw", "0.01")
        ch_r = get_setting("ch_reward", "0.004")
        daily_b = get_setting("daily_bonus", "0.005")
        btns = [
            [{"text": "💰 زيادة رصيد", "callback_data": "admin_add_bal"}, {"text": "📢 إذاعة", "callback_data": "admin_broadcast"}],
            [{"text": f"⚙️ الحد الأدنى ({min_w})", "callback_data": "admin_set_min_w"}, {"text": f"⚙️ مكافأة القنوات ({ch_r})", "callback_data": "admin_set_ch_r"}],
            [{"text": f"⚙️ الهدية اليومية ({daily_b})", "callback_data": "admin_set_daily_b"}, {"text": "⚙️ نظام الإحالات (3 أجيال)", "callback_data": "admin_manage_refs"}],
            [{"text": "📝 تعديل الدعم الفني", "callback_data": "admin_set_support"}, {"text": "👥 مراقبة المحتالين", "callback_data": "admin_top_refs"}],
            [{"text": "➕ قناة إجبارية", "callback_data": "admin_add_main_ch"}, {"text": "📢 قناة ربح", "callback_data": "admin_add_speed_ch"}],
            [{"text": "🔗 مهمة رابط", "callback_data": "admin_add_shortlink"}, {"text": "👑 مشرف فرعي", "callback_data": "admin_add_admin"}],
            [{"text": "🗑️ إدارة القنوات", "callback_data": "admin_manage_channels"}, {"text": "🗑️ المهام", "callback_data": "admin_manage_tasks"}]
        ]
        return send_msg(chat_id, get_text(lang, 'admin_panel'), {"inline_keyboard": btns})

    # ================= حالات الانتظار والفلاتر الأمنية =================
    if state == 'wait_wallet':
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        wallet_str = text.strip()
        is_doge_address = wallet_str.startswith("D") and len(wallet_str) >= 30 and wallet_str.isalnum()
        is_fp_email = "@" in wallet_str and "." in wallet_str
        if not (is_doge_address or is_fp_email):
            err_msg = "❌ <b>عنوان غير صالح!</b>\nيرجى إرسال عنوان Dogecoin صحيح أو إيميل FaucetPay." if lang == 'ar' else "❌ <b>Invalid Address!</b>\nSend a valid DOGE address or FaucetPay email."
            return send_msg(chat_id, err_msg)
        
        user = calculate_and_update_mining(user)
        for adm in supabase.table("admins").select("user_id").execute().data:
            send_msg(adm['user_id'], f"🔔 <b>طلب سحب عاجل!</b>\n👤 آيدي: <code>{user_id}</code>\n💰 الرصيد: <code>{user['balance']:.8f}</code>\n🏦 المحفظة:\n<code>{wallet_str}</code>")
        supabase.table("withdrawals").insert({"user_id": user_id, "amount": user['balance'], "wallet": wallet_str, "status": "pending", "created_at": now}).execute()
        update_user(user_id, {"balance": 0.0, "state": "idle"})
        return send_msg(chat_id, get_text(lang, 'withdraw_done'))

    elif state.startswith('wait_pass_'):
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        task_id = int(state.split('_')[2])
        t_res = supabase.table("shortlinks").select("*").eq("id", task_id).execute()
        if t_res.data and text.strip() == t_res.data[0]['password']:
            reward = float(t_res.data[0]['reward'])
            update_user(user_id, {"balance": float(user['balance']) + reward, "state": "idle"})
            supabase.table("claimed_tasks").upsert({"user_id": user_id, "task_id": task_id, "claimed_at": now}).execute()
            send_msg(chat_id, f"🎉 <b>رائع!</b> تمت إضافة <code>{reward:.8f}</code> DOGE.")
        else:
            update_user(user_id, {"state": "idle"})
            send_msg(chat_id, "❌ <b>كلمة السر خاطئة!</b>")
        return

    # إعدادات الإدارة
    elif state == 'admin_broadcast' and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        for u in supabase.table("users").select("user_id").execute().data:
            try: send_msg(u['user_id'], f"📢 <b>إعلان رسمي:</b>\n\n{text}")
            except: pass
        update_user(user_id, {"state": "idle"})
        return send_msg(chat_id, "✅ تم إرسال الإذاعة.")
    elif state == 'admin_set_min_w' and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        set_setting("min_withdraw", float(text.strip()))
        update_user(user_id, {"state": "idle"})
        return send_msg(chat_id, f"✅ تم تحديث الحد الأدنى.")
    elif state == 'admin_set_ch_r' and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        set_setting("ch_reward", float(text.strip()))
        update_user(user_id, {"state": "idle"})
        return send_msg(chat_id, f"✅ تم تحديث مكافأة القنوات.")
    elif state == 'admin_set_daily_b' and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        set_setting("daily_bonus", float(text.strip()))
        update_user(user_id, {"state": "idle"})
        return send_msg(chat_id, f"✅ تم تحديث الهدية اليومية.")
    
    # حالات إعداد نسب الإحالة
    elif state == 'admin_set_t1' and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        set_setting("ref_t1", float(text.strip())); update_user(user_id, {"state": "idle"})
        return send_msg(chat_id, f"✅ تم تحديث نسبة الجيل الأول.")
    elif state == 'admin_set_t2' and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        set_setting("ref_t2", float(text.strip())); update_user(user_id, {"state": "idle"})
        return send_msg(chat_id, f"✅ تم تحديث نسبة الجيل الثاني.")
    elif state == 'admin_set_t3' and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        set_setting("ref_t3", float(text.strip())); update_user(user_id, {"state": "idle"})
        return send_msg(chat_id, f"✅ تم تحديث نسبة الجيل الثالث.")

    elif state == 'admin_set_support' and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        set_setting(f"support_text_{lang}", text)
        update_user(user_id, {"state": "idle"})
        return send_msg(chat_id, "✅ تم تحديث رسالة الدعم الفني.")
    elif state in ['admin_add_main_ch', 'admin_add_speed_ch'] and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        ch_type = 'main' if state == 'admin_add_main_ch' else 'speed'
        ch_id = str(msg['forward_from_chat']['id']) if 'forward_from_chat' in msg else text.split()[1] if len(text.split())>1 else text
        if not ch_id.startswith("-") and not ch_id.startswith("@"): ch_id = "@" + ch_id
        test = call_api("getChat", {"chat_id": ch_id})
        if test and test.get('ok'):
            supabase.table("channels").insert({"name": test['result'].get('title', 'قناة'), "url": test['result'].get('invite_link') or f"https://t.me/{test['result'].get('username', '')}", "ch_id": str(ch_id), "type": ch_type}).execute()
            send_msg(chat_id, "✅ تمت إضافة القناة بنجاح.")
        else: send_msg(chat_id, "❌ البوت ليس مشرفاً في القناة أو المعرف خطأ.")
        return update_user(user_id, {"state": "idle"})
    elif state == 'admin_add_shortlink' and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        parts = text.split('|')
        if len(parts) == 4:
            supabase.table("shortlinks").insert({"description": parts[0].strip(), "url": parts[1].strip(), "password": parts[2].strip(), "reward": float(parts[3].strip())}).execute()
            send_msg(chat_id, "✅ تمت الإضافة.")
        return update_user(user_id, {"state": "idle"})
    elif state == 'admin_wait_bal_id' and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        update_user(user_id, {"state": f'admin_wait_bal_amt_{text}'})
        return send_msg(chat_id, "💰 أرسل المبلغ:")
    elif state.startswith('admin_wait_bal_amt_') and user_is_admin:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        t_id = int(state.split('_')[4])
        t_user = get_user(t_id)
        if t_user:
            update_user(t_id, {"balance": float(t_user.get('balance',0)) + float(text)})
            send_msg(chat_id, "✅ تمت الإضافة.")
        return update_user(user_id, {"state": "idle"})
    elif state == 'admin_wait_admin_id' and user_id == OWNER_ID:
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        supabase.table("admins").upsert({"user_id": int(text)}).execute()
        update_user(user_id, {"state": "idle"})
        return send_msg(chat_id, "✅ تم تعيين المشرف.")

# ================= معالجة الأزرار المدمجة =================
def process_callback(cq):
    chat_id, user_id, data, msg_id = cq['message']['chat']['id'], cq['from']['id'], cq.get('data', ''), cq['message']['message_id']
    call_api("answerCallbackQuery", {"callback_query_id": cq['id']})

    user = get_user(user_id)
    lang = user.get('lang', 'en') if user else 'en'
    user_is_admin = is_admin(user_id)

    if data == "cap_ok":
        if user and user.get('captcha_passed', 0) == 0 and user.get('referrer_id'):
            # 🛑 التوزيع الهرمي للإحالات (3 أجيال) بشكل آمن ومصدري 🛑
            t1_id = user['referrer_id']
            base_speed = 0.0000000115
            
            t1_p = float(get_setting("ref_t1", "50"))
            t2_p = float(get_setting("ref_t2", "20"))
            t3_p = float(get_setting("ref_t3", "5"))

            # الجيل الأول
            t1_user = get_user(t1_id)
            if t1_user:
                new_s1 = float(t1_user['speed']) + (base_speed * (t1_p / 100.0))
                update_user(t1_id, {"speed": new_s1, "ref_count": int(t1_user['ref_count']) + 1})
                send_msg(t1_id, get_text(t1_user.get('lang', 'en'), 'ref_notify', level=1, ref_p=t1_p))
                
                # الجيل الثاني
                t2_id = t1_user.get('referrer_id')
                if t2_id and t2_id != 0:
                    t2_user = get_user(t2_id)
                    if t2_user:
                        new_s2 = float(t2_user['speed']) + (base_speed * (t2_p / 100.0))
                        update_user(t2_id, {"speed": new_s2})
                        send_msg(t2_id, get_text(t2_user.get('lang', 'en'), 'ref_notify', level=2, ref_p=t2_p))
                        
                        # الجيل الثالث
                        t3_id = t2_user.get('referrer_id')
                        if t3_id and t3_id != 0:
                            t3_user = get_user(t3_id)
                            if t3_user:
                                new_s3 = float(t3_user['speed']) + (base_speed * (t3_p / 100.0))
                                update_user(t3_id, {"speed": new_s3})
                                send_msg(t3_id, get_text(t3_user.get('lang', 'en'), 'ref_notify', level=3, ref_p=t3_p))

        update_user(user_id, {"captcha_passed": 1})
        delete_msg(chat_id, msg_id)
        
        main_channels = supabase.table("channels").select("*").eq("type", "main").execute().data
        unjoined = [ch for ch in main_channels if ch.get('ch_id') and not check_sub(user_id, ch['ch_id'])]
        if unjoined:
            markup = {"inline_keyboard": [[{"text": f"📢 Join {ch['name']}", "url": ch['url']}] for ch in unjoined]}
            markup["inline_keyboard"].append([{"text": "✅ Verify / تحقق", "callback_data": "check_main_sub"}])
            send_msg(chat_id, get_text(lang, 'sub_req'), markup)
        else:
            send_msg(chat_id, "✅ " + get_text(lang, 'captcha_ok'), get_reply_keyboard(lang, user_is_admin))
            user = calculate_and_update_mining(get_user(user_id))
            send_msg(chat_id, get_text(lang, 'main_menu', balance=float(user['balance']), speed=float(user['speed'])*86400, refs=int(user['ref_count'])))

    elif data == "check_main_sub":
        main_channels = supabase.table("channels").select("*").eq("type", "main").execute().data
        if all(check_sub(user_id, ch['ch_id']) for ch in main_channels if ch.get('ch_id')):
            delete_msg(chat_id, msg_id)
            send_msg(chat_id, "✅ تم التحقق!", get_reply_keyboard(lang, user_is_admin))
            user = calculate_and_update_mining(get_user(user_id))
            send_msg(chat_id, get_text(lang, 'main_menu', balance=float(user['balance']), speed=float(user['speed'])*86400, refs=int(user['ref_count'])))
        else:
            call_api("answerCallbackQuery", {"callback_query_id": cq['id'], "text": "❌ اشترك في جميع القنوات أولاً!", "show_alert": True})

    elif data.startswith("verify_reward_"):
        ch_id_pk = int(data.split("_")[2])
        ch_row = supabase.table("channels").select("*").eq("id", ch_id_pk).execute().data
        if ch_row and check_sub(user_id, ch_row[0]['ch_id']):
            reward = float(get_setting("ch_reward", "0.004"))
            update_user(user_id, {"balance": float(user.get('balance', 0)) + reward})
            supabase.table("joined_speed_channels").upsert({"user_id": user_id, "ch_id": ch_id_pk}).execute()
            send_msg(chat_id, f"🎉 <b>مبروك!</b> استلمت مكافأة {reward} DOGE!")
        else: send_msg(chat_id, "❌ لم تشترك في القناة بعد!")

    elif data.startswith("enter_pass_"):
        update_user(user_id, {"state": f"wait_pass_{data.split('_')[2]}"})
        send_msg(chat_id, f"🔑 <b>أرسل الآن كلمة السر:</b>")

    # أزرار الإدارة
    elif data == "admin_manage_refs" and user_is_admin:
        t1 = get_setting("ref_t1", "50")
        t2 = get_setting("ref_t2", "20")
        t3 = get_setting("ref_t3", "5")
        btns = [
            [{"text": f"🥇 الجيل الأول ({t1}%)", "callback_data": "admin_set_t1"}],
            [{"text": f"🥈 الجيل الثاني ({t2}%)", "callback_data": "admin_set_t2"}],
            [{"text": f"🥉 الجيل الثالث ({t3}%)", "callback_data": "admin_set_t3"}],
            [{"text": "🔙 رجوع", "callback_data": "admin_back"}]
        ]
        send_msg(chat_id, "⚙️ <b>اختر الجيل الذي تريد تعديل نسبته المئوية:</b>", {"inline_keyboard": btns})
    
    elif data == "admin_back" and user_is_admin:
        # يرجع يعرض القائمة الرئيسية للإدارة
        min_w = get_setting("min_withdraw", "0.01")
        ch_r = get_setting("ch_reward", "0.004")
        daily_b = get_setting("daily_bonus", "0.005")
        btns = [
            [{"text": "💰 زيادة رصيد", "callback_data": "admin_add_bal"}, {"text": "📢 إذاعة", "callback_data": "admin_broadcast"}],
            [{"text": f"⚙️ الحد الأدنى ({min_w})", "callback_data": "admin_set_min_w"}, {"text": f"⚙️ مكافأة القنوات ({ch_r})", "callback_data": "admin_set_ch_r"}],
            [{"text": f"⚙️ الهدية اليومية ({daily_b})", "callback_data": "admin_set_daily_b"}, {"text": "⚙️ نظام الإحالات (3 أجيال)", "callback_data": "admin_manage_refs"}],
            [{"text": "📝 تعديل الدعم الفني", "callback_data": "admin_set_support"}, {"text": "👥 مراقبة المحتالين", "callback_data": "admin_top_refs"}],
            [{"text": "➕ قناة إجبارية", "callback_data": "admin_add_main_ch"}, {"text": "📢 قناة ربح", "callback_data": "admin_add_speed_ch"}],
            [{"text": "🔗 مهمة رابط", "callback_data": "admin_add_shortlink"}, {"text": "👑 مشرف فرعي", "callback_data": "admin_add_admin"}],
            [{"text": "🗑️ إدارة القنوات", "callback_data": "admin_manage_channels"}, {"text": "🗑️ المهام", "callback_data": "admin_manage_tasks"}]
        ]
        send_msg(chat_id, get_text(lang, 'admin_panel'), {"inline_keyboard": btns})

    elif data == "admin_set_t1" and user_is_admin:
        update_user(user_id, {"state": "admin_set_t1"}); send_msg(chat_id, "⚙️ أرسل نسبة الجيل الأول كـ رقم (مثال: 50):")
    elif data == "admin_set_t2" and user_is_admin:
        update_user(user_id, {"state": "admin_set_t2"}); send_msg(chat_id, "⚙️ أرسل نسبة الجيل الثاني كـ رقم (مثال: 20):")
    elif data == "admin_set_t3" and user_is_admin:
        update_user(user_id, {"state": "admin_set_t3"}); send_msg(chat_id, "⚙️ أرسل نسبة الجيل الثالث كـ رقم (مثال: 5):")

    elif data == "admin_broadcast" and user_is_admin:
        update_user(user_id, {"state": "admin_broadcast"}); send_msg(chat_id, "📢 <b>أرسل الرسالة للإذاعة:</b>")
    elif data == "admin_set_min_w" and user_is_admin:
        update_user(user_id, {"state": "admin_set_min_w"}); send_msg(chat_id, "⚙️ أرسل الحد الأدنى الجديد:")
    elif data == "admin_set_ch_r" and user_is_admin:
        update_user(user_id, {"state": "admin_set_ch_r"}); send_msg(chat_id, "⚙️ أرسل قيمة المكافأة للقنوات:")
    elif data == "admin_set_daily_b" and user_is_admin:
        update_user(user_id, {"state": "admin_set_daily_b"}); send_msg(chat_id, "⚙️ أرسل قيمة الهدية اليومية:")
    elif data == "admin_set_support" and user_is_admin:
        update_user(user_id, {"state": "admin_set_support"}); send_msg(chat_id, "📝 أرسل رسالة الدعم الفني الجديدة:")
    elif data == "admin_top_refs" and user_is_admin:
        top_list = supabase.table("users").select("*").gt("ref_count", 10).order("ref_count", desc=True).limit(30).execute().data
        if top_list: send_msg(chat_id, "👥 <b>المتفاعلون (>10):</b>\n" + "".join([f"👤 {t['user_id']} | 👥 {t['ref_count']} | 💰 {float(t['balance']):.4f}\n" for t in top_list]))
    elif data == "admin_add_main_ch" and user_is_admin:
        update_user(user_id, {"state": "admin_add_main_ch"}); send_msg(chat_id, "➕ <b>إضافة قناة إجبارية:</b> أرسل المعرف أو وجه رسالة.")
    elif data == "admin_add_speed_ch" and user_is_admin:
        update_user(user_id, {"state": "admin_add_speed_ch"}); send_msg(chat_id, "📢 <b>إضافة قناة ربح:</b> أرسل المعرف أو وجه رسالة.")
    elif data == "admin_add_shortlink" and user_is_admin:
        update_user(user_id, {"state": "admin_add_shortlink"}); send_msg(chat_id, "🔗 أرسل: <code>الوصف | الرابط | كلمة_السر | المكافأة</code>")
    elif data == "admin_manage_channels" and user_is_admin:
        for ch in supabase.table("channels").select("*").execute().data: send_msg(chat_id, f"📢 {ch['name']}", {"inline_keyboard": [[{"text": f"❌ حذف", "callback_data": f"del_ch_{ch['id']}"}]]})
    elif data.startswith("del_ch_") and user_is_admin:
        supabase.table("channels").delete().eq("id", int(data.split("_")[2])).execute(); send_msg(chat_id, "✅ تم الحذف.")
    elif data == "admin_manage_tasks" and user_is_admin:
        for t in supabase.table("shortlinks").select("*").execute().data: send_msg(chat_id, f"📌 {t['description']}", {"inline_keyboard": [[{"text": f"❌ حذف", "callback_data": f"del_task_{t['id']}"}]]})
    elif data.startswith("del_task_") and user_is_admin:
        supabase.table("shortlinks").delete().eq("id", int(data.split("_")[2])).execute(); send_msg(chat_id, "✅ تم الحذف.")
    elif data == "admin_add_bal" and user_is_admin:
        update_user(user_id, {"state": "admin_wait_bal_id"}); send_msg(chat_id, "💰 أرسل آيدي المستخدم:")
    elif data == "admin_add_admin" and user_id == OWNER_ID:
        update_user(user_id, {"state": "admin_wait_admin_id"}); send_msg(chat_id, "👑 أرسل آيدي المشرف الجديد:")

# ================= ممر Vercel Serverless =================
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            if body:
                data = json.loads(body.decode('utf-8'))
                if 'message' in data: process_message(data['message'])
                elif 'callback_query' in data: process_callback(data['callback_query'])
        except Exception:
            try: send_msg(OWNER_ID, f"⚠️️ <b>Crash Trace:</b>\n<code>{traceback.format_exc()[-600:]}</code>")
            except: pass
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Active")
