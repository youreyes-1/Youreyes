from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import time
import random
import traceback
import math
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
        'btn_earn_hub': "🎯 Tasks & Earn",
        'btn_daily_bonus': "🎁 Daily Bonus",
        'btn_about': "🖥 Mining Hardware",
        'btn_stats': "📊 Network Stats",
        'btn_calc': "🧮 Profit Calculator",
        'btn_support': "📞 Support",
        'btn_lang': "🌐 العربية",
        'btn_admin': "👑 Admin Panel",
        'captcha_msg': "🤖 <b>Anti-Bot System:</b>\nClick the unique symbol (🔴) to authenticate.",
        'captcha_ok': "Human verification successful!",
        'sub_req': "⚠ <b>Action Required!</b>\nJoin ALL our official channels below to unlock your miner:",
        'main_menu': "⛏ <b>Active Mining Servers</b>\n\n💰 Live Balance: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ Hash Power: <code>{speed:.8f}</code> DOGE/Day\n👥 Direct Team: <code>{refs}</code>\n\n<i>🟢 Server Status: Online & Stable (Cloud).</i>",
        'team_msg': "👥 <b>Multi-Tier Partner Program:</b>\nBuild your network and earn from 3 levels deep!\n\n🥇 Tier 1 (Direct): <b>+{t1}%</b> speed\n🥈 Tier 2: <b>+{t2}%</b> speed\n🥉 Tier 3: <b>+{t3}%</b> speed\n\n📊 Direct Invites: <code>{refs}</code>\n🔗 Your Referral Link:\n<code>{link}</code>",
        'withdraw_err': "❌ Balance is below the minimum threshold ({min} DOGE).",
        'withdraw_req': "💸 <b>Secure Withdrawal:</b>\nSend your <b>Dogecoin (FaucetPay)</b> wallet address:",
        'withdraw_done': "✅ <b>Request Logged!</b>\nYour payout is under review.",
        'ref_notify': "🎉 <b>Great News!</b>\nA user joined your network (Tier {level}). Speed increased by {ref_p}%!"
    },
    'ar': {
        'btn_refresh': "🔄 تحديث الأرباح",
        'btn_withdraw': "💸 سحب الرصيد",
        'btn_team': "👥 فريقك (3 أجيال)",
        'btn_earn_hub': "🎯 المهام والربح",
        'btn_daily_bonus': "🎁 الهدية اليومية",
        'btn_about': "🖥 عتاد التعدين",
        'btn_stats': "📊 إحصائيات المنجم",
        'btn_calc': "🧮 حاسبة الأرباح",
        'btn_support': "📞 الدعم الفني",
        'btn_lang': "🌐 English",
        'btn_admin': "👑 الإدارة (للمشرفين)",
        'captcha_msg': "🤖 <b>نظام الحماية (Anti-Bot):</b>\nاضغط على الرمز المختلف (🔴) للبدء.",
        'captcha_ok': "تم التحقق البشري بنجاح!",
        'sub_req': "⚠️ <b>شرط أساسي!</b>\nيجب عليك الاشتراك في جميع القنوات أدناه لتفعيل حسابك:",
        'main_menu': "⛏ <b>خوادم التعدين النشطة</b>\n\n💰 الرصيد المباشر: <code>{balance:.8f}</code> <b>DOGE</b>\n⚡ قوة التعدين: <code>{speed:.8f}</code> DOGE/يوم\n👥 إحالاتك المباشرة: <code>{refs}</code>\n\n<i>🟢 حالة الخادم: متصل ومستقر (سحابي).</i>",
        'team_msg': "👥 <b>نظام الإحالات الهرمي (3 أجيال):</b>\nابنِ شبكتك واربح من دعوات أصدقائك وأصدقاء أصدقائك!\n\n🥇 الجيل الأول (مباشر): <b>+{t1}%</b> سرعة\n🥈 الجيل الثاني: <b>+{t2}%</b> سرعة\n🥉 الجيل الثالث: <b>+{t3}%</b> سرعة\n\n📊 إحالاتك المباشرة: <code>{refs}</code> عضو\n🔗 رابط الدعوة الخاص بك:\n<code>{link}</code>",
        'withdraw_err': "❌ رصيدك الحالي أقل من الحد الأدنى للسحب ({min} DOGE).",
        'withdraw_req': "💸 <b>بوابة السحب الآمنة:</b>\nأرسل عنوان محفظة <b>Dogecoin (FaucetPay)</b> (يبدأ بحرف D أو الإيميل):",
        'withdraw_done': "✅ <b>تم استلام طلب السحب!</b>\nالطلب قيد المراجعة المالية.",
        'ref_notify': "🎉 <b>أخبار ممتازة!</b>\nانضم شخص لشبكتك (من الجيل {level}). زادت سرعتك بنسبة {ref_p}%!"
    }
}

# ================= أدوات التخزين =================
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

def edit_msg(chat_id, msg_id, text, markup=None):
    payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if markup: payload["reply_markup"] = markup
    return call_api("editMessageText", payload)

def check_sub(user_id, channel_id):
    if not channel_id: return True
    res = call_api("getChatMember", {"chat_id": channel_id, "user_id": user_id})
    if res and res.get('ok'): return res['result']['status'] in ['member', 'administrator', 'creator']
    return False

def get_text(lang, key, **kwargs):
    text = LANG.get(lang, LANG['en']).get(key, "")
    return text.format(**kwargs) if kwargs else text

def get_reply_keyboard(lang, user_is_admin):
    kb = [
        [{"text": get_text(lang, 'btn_earn_hub')}],
        [{"text": get_text(lang, 'btn_refresh')}, {"text": get_text(lang, 'btn_withdraw')}],
        [{"text": get_text(lang, 'btn_team')}, {"text": get_text(lang, 'btn_daily_bonus')}],
        [{"text": get_text(lang, 'btn_calc')}, {"text": get_text(lang, 'btn_stats')}],
        [{"text": get_text(lang, 'btn_about')}, {"text": get_text(lang, 'btn_support')}],
        [{"text": get_text(lang, 'btn_lang')}]
    ]
    if user_is_admin: kb.insert(0, [{"text": get_text(lang, 'btn_admin')}])
    return {"keyboard": kb, "resize_keyboard": True}

def calculate_and_update_mining(user):
    now = int(time.time())
    bal, speed = float(user.get('balance', 0.0)), float(user.get('speed', 0.0000000115))
    earned = (now - int(user.get('last_update') or now)) * speed
    if earned > 0:
        user['balance'] = bal + earned; user['last_update'] = now
        update_user(user['user_id'], {"balance": user['balance'], "last_update": now})
    return user

# ================= معالجة الرسائل =================
def process_message(msg):
    chat_id, user_id, text = msg['chat']['id'], msg['from']['id'], msg.get('text', '')
    now = int(time.time())

    user_is_admin = is_admin(user_id)
    user = get_user(user_id)
    
    if not user:
        ref_id = int(text.split(" ")[1]) if text.startswith("/start ") and text.split(" ")[1].isdigit() else 0
        user = {"user_id": user_id, "balance": 0.0, "speed": 0.0000000115, "last_update": now, "captcha_passed": 1 if user_is_admin else 0, "referrer_id": ref_id, "ref_count": 0, "state": "idle", "lang": "en"}
        supabase.table("users").upsert(user).execute()
    elif user_is_admin and user.get('captcha_passed') == 0:
        update_user(user_id, {"captcha_passed": 1})
        user['captcha_passed'] = 1

    lang, state = user.get('lang', 'en'), user.get('state', 'idle')

    if user.get('captcha_passed', 0) == 0 and not user_is_admin:
        btns = [{"text": "🔹", "callback_data": "cap_fail"} for _ in range(3)]
        btns.insert(random.randint(0, 3), {"text": "🔴", "callback_data": "cap_ok"})
        return send_msg(chat_id, get_text(lang, 'captcha_msg'), {"inline_keyboard": [btns]})

    if not user_is_admin:
        main_channels = supabase.table("channels").select("*").eq("type", "main").execute().data
        unjoined = [ch for ch in main_channels if ch.get('ch_id') and not check_sub(user_id, ch['ch_id'])]
        if unjoined:
            markup = {"inline_keyboard": [[{"text": f"📢 Join {ch['name']}", "url": ch['url']}] for ch in unjoined]}
            markup["inline_keyboard"].append([{"text": "✅ Verify / تحقق", "callback_data": "check_main_sub"}])
            return send_msg(chat_id, get_text(lang, 'sub_req'), markup)

    system_btns = [get_text(lang, k) for k in ['btn_refresh', 'btn_withdraw', 'btn_team', 'btn_earn_hub', 'btn_daily_bonus', 'btn_lang', 'btn_about', 'btn_stats', 'btn_calc', 'btn_support', 'btn_admin']]

    if text == get_text(lang, 'btn_refresh') or text == "/start":
        user = calculate_and_update_mining(user)
        if text == "/start": send_msg(chat_id, "✅", get_reply_keyboard(lang, user_is_admin))
        return send_msg(chat_id, get_text(lang, 'main_menu', balance=float(user['balance']), speed=float(user['speed'])*86400, refs=int(user['ref_count'])))

    elif text == get_text(lang, 'btn_lang'):
        new_lang = 'ar' if lang == 'en' else 'en'
        update_user(user_id, {"lang": new_lang})
        send_msg(chat_id, "🌐 تم تغيير اللغة / Language Updated", get_reply_keyboard(new_lang, user_is_admin))
        return send_msg(chat_id, get_text(new_lang, 'main_menu', balance=float(user['balance']), speed=float(user['speed'])*86400, refs=int(user['ref_count'])))

    # ================= المركز المجمع للمهام والربح =================
    elif text == get_text(lang, 'btn_earn_hub'):
        user = calculate_and_update_mining(user)
        msg_text = f"💰 <b>رصيدك:</b> <code>{user['balance']:.8f}</code> DOGE\n\n🎯 <b>اختر طريقة الربح التي تفضلها:</b>" if lang == 'ar' else f"💰 <b>Balance:</b> <code>{user['balance']:.8f}</code> DOGE\n\n🎯 <b>Select an earning method:</b>"
        btns = [
            [{"text": "📢 الاشتراك في القنوات", "callback_data": "open_ch_page_0"}],
            [{"text": "🔗 تخطي الروابط المختصرة", "callback_data": "open_task_page_0"}]
        ]
        return send_msg(chat_id, msg_text, {"inline_keyboard": btns})

    elif text == get_text(lang, 'btn_withdraw'):
        user = calculate_and_update_mining(user)
        joined_channels = supabase.table("joined_speed_channels").select("*").eq("user_id", user_id).execute().data
        if joined_channels:
            active_reward_channels = supabase.table("channels").select("*").eq("type", "speed").execute().data
            active_dict = {ch['id']: ch['name'] for ch in active_reward_channels}
            ch_tg_ids = {ch['id']: ch['ch_id'] for ch in active_reward_channels}
            penalty = float(get_setting("ch_reward", "0.004")) * 2
            penalized = False
            for jc in joined_channels:
                if jc['ch_id'] in active_dict:
                    if not check_sub(user_id, ch_tg_ids[jc['ch_id']]): 
                        user['balance'] -= penalty
                        update_user(user_id, {"balance": user['balance']})
                        supabase.table("joined_speed_channels").delete().eq("user_id", user_id).eq("ch_id", jc['ch_id']).execute()
                        penalized = True
                        send_msg(chat_id, f"🚨 <b>تحذير أمني!</b>\nغادرت القناة ({active_dict[jc['ch_id']]}). تم خصم <code>{penalty:.4f}</code> DOGE كعقوبة." if lang == 'ar' else f"🚨 <b>Penalty!</b> You left ({active_dict[jc['ch_id']]}). Deducted: <code>{penalty:.4f}</code> DOGE.")
            if penalized: return

        min_w = float(get_setting("min_withdraw", "0.01"))
        if float(user['balance']) < min_w: return send_msg(chat_id, get_text(lang, 'withdraw_err', min=min_w))
        update_user(user_id, {"state": "wait_wallet"})
        return send_msg(chat_id, get_text(lang, 'withdraw_req'))

    elif text == get_text(lang, 'btn_team'):
        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        t1, t2, t3 = get_setting("ref_t1", "50"), get_setting("ref_t2", "20"), get_setting("ref_t3", "5")
        return send_msg(chat_id, get_text(lang, 'team_msg', t1=t1, t2=t2, t3=t3, refs=int(user['ref_count']), link=link))

    elif text == get_text(lang, 'btn_daily_bonus'):
        c_res = supabase.table("claimed_tasks").select("claimed_at").eq("user_id", user_id).eq("task_id", 0).execute()
        if c_res.data and (now - c_res.data[0]['claimed_at'] < 86400):
            rem = 86400 - (now - c_res.data[0]['claimed_at'])
            return send_msg(chat_id, f"⏳ {'عد بعد' if lang=='ar' else 'Come back in'} {rem//3600}h {(rem%3600)//60}m.")
        daily_b = float(get_setting("daily_bonus", "0.005"))
        update_user(user_id, {"balance": float(user['balance']) + daily_b})
        supabase.table("claimed_tasks").upsert({"user_id": user_id, "task_id": 0, "claimed_at": now}).execute()
        return send_msg(chat_id, f"🎉 {'حصلت على الهدية:' if lang=='ar' else 'Daily bonus:'} {daily_b} DOGE")

    elif text == get_text(lang, 'btn_admin') and user_is_admin:
        btns = [
            [{"text": "📈 إحصائيات", "callback_data": "admin_real_stats"}, {"text": "💰 رصيد", "callback_data": "admin_add_bal"}],
            [{"text": "📢 إذاعة", "callback_data": "admin_broadcast"}, {"text": "⚙️ نظام الإحالات", "callback_data": "admin_manage_refs"}],
            [{"text": "➕ قناة إجبارية", "callback_data": "admin_add_main_ch"}, {"text": "📢 قناة ربح", "callback_data": "admin_add_speed_ch"}],
            [{"text": "🔗 مهمة رابط", "callback_data": "admin_add_shortlink"}, {"text": "🗑 قنوات", "callback_data": "admin_manage_channels"}]
        ]
        return send_msg(chat_id, get_text(lang, 'admin_panel'), {"inline_keyboard": btns})

    # إدخال المحفظة
    if state == 'wait_wallet':
        if text in system_btns: return update_user(user_id, {"state": "idle"})
        wallet_str = text.strip()
        if not ((wallet_str.startswith("D") and len(wallet_str) >= 30) or ("@" in wallet_str and "." in wallet_str)):
            return send_msg(chat_id, "❌ <b>عنوان غير صالح!</b>" if lang == 'ar' else "❌ <b>Invalid Address!</b>")
        user = calculate_and_update_mining(user)
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
            send_msg(chat_id, f"🎉 <b>تمت إضافة <code>{reward:.8f}</code> DOGE.</b>")
        else:
            update_user(user_id, {"state": "idle"})
            send_msg(chat_id, "❌ <b>كلمة السر خاطئة!</b>")

# ================= معالجة الأزرار المدمجة =================
def process_callback(cq):
    chat_id, user_id, data, msg_id = cq['message']['chat']['id'], cq['from']['id'], cq.get('data', ''), cq['message']['message_id']
    user = get_user(user_id)
    lang = user.get('lang', 'en') if user else 'en'
    user_is_admin = is_admin(user_id)
    now = int(time.time())

    if data == "cap_ok":
        call_api("answerCallbackQuery", {"callback_query_id": cq['id']})
        update_user(user_id, {"captcha_passed": 1}); delete_msg(chat_id, msg_id)
        send_msg(chat_id, "✅ " + get_text(lang, 'captcha_ok'), get_reply_keyboard(lang, user_is_admin))
        return

    # ================= واجهة القنوات الجديدة المتطورة =================
    if data.startswith("open_ch_page_"):
        page = int(data.split("_")[3])
        user = calculate_and_update_mining(user)
        
        # جلب القنوات غير المشترك فيها فقط (عشان اللستة تنظف)
        all_ch = supabase.table("channels").select("*").eq("type", "speed").execute().data
        joined = [jc['ch_id'] for jc in supabase.table("joined_speed_channels").select("ch_id").eq("user_id", user_id).execute().data]
        pending_ch = [ch for ch in all_ch if ch['id'] not in joined]
        
        if not pending_ch:
            call_api("answerCallbackQuery", {"callback_query_id": cq['id'], "text": "✅ لقد أكملت جميع القنوات المتاحة!", "show_alert": True})
            return edit_msg(chat_id, msg_id, f"💰 <b>رصيدك:</b> <code>{user['balance']:.8f}</code> DOGE\n\n🎉 لا توجد قنوات جديدة حالياً.")

        total_pages = math.ceil(len(pending_ch) / 5)
        page_channels = pending_ch[page*5 : (page+1)*5]
        
        msg_text = f"💰 <b>رصيدك:</b> <code>{user['balance']:.8f}</code> DOGE\n\n"
        msg_text += "<b>الخطوات:</b>\n❶ اشترك في كل القنوات أدناه.\n❷ اضغط على تحقق ✅." if lang == 'ar' else "<b>Steps:</b>\n❶ Join channels below.\n❷ Click Verify ✅."
        
        btns = []
        for ch in page_channels:
            # الترتيب: العلم على اليسار، واسم القناة على اليمين (حسب الصورة)
            btns.append([
                {"text": "🚩", "callback_data": f"report_ch_{ch['id']}"},
                {"text": f"↗️ {ch['name']}", "url": ch['url']}
            ])
            
        # أزرار التنقل بين الصفحات
        nav_row = []
        if page > 0: nav_row.append({"text": "⬅️ السابق", "callback_data": f"open_ch_page_{page-1}"})
        nav_row.append({"text": f"صفحة {page+1}/{total_pages}", "callback_data": "ignore"})
        if page < total_pages - 1: nav_row.append({"text": "التالي ➡️", "callback_data": f"open_ch_page_{page+1}"})
        if nav_row: btns.append(nav_row)
        
        # زر التحقق الشامل
        verify_text = "✅ تحقق من الاشتراكات" if lang == 'ar' else "✅ Verify Subscriptions"
        btns.append([{"text": verify_text, "callback_data": f"bulk_verify_{page}"}])
        btns.append([{"text": "🔙 رجوع", "callback_data": "back_to_hub"}])
        
        edit_msg(chat_id, msg_id, msg_text, {"inline_keyboard": btns})
        call_api("answerCallbackQuery", {"callback_query_id": cq['id']})

    elif data == "back_to_hub":
        user = calculate_and_update_mining(user)
        msg_text = f"💰 <b>رصيدك:</b> <code>{user['balance']:.8f}</code> DOGE\n\n🎯 <b>اختر طريقة الربح التي تفضلها:</b>" if lang == 'ar' else f"💰 <b>Balance:</b> <code>{user['balance']:.8f}</code> DOGE\n\n🎯 <b>Select an earning method:</b>"
        btns = [[{"text": "📢 الاشتراك في القنوات", "callback_data": "open_ch_page_0"}], [{"text": "🔗 تخطي الروابط المختصرة", "callback_data": "open_task_page_0"}]]
        edit_msg(chat_id, msg_id, msg_text, {"inline_keyboard": btns})
        call_api("answerCallbackQuery", {"callback_query_id": cq['id']})

    # ================= التحقق الشامل للقنوات =================
    elif data.startswith("bulk_verify_"):
        page = int(data.split("_")[2])
        all_ch = supabase.table("channels").select("*").eq("type", "speed").execute().data
        joined = [jc['ch_id'] for jc in supabase.table("joined_speed_channels").select("ch_id").eq("user_id", user_id).execute().data]
        pending_ch = [ch for ch in all_ch if ch['id'] not in joined]
        page_channels = pending_ch[page*5 : (page+1)*5]
        
        reward_val = float(get_setting("ch_reward", "0.004"))
        success_count = 0
        
        for ch in page_channels:
            if check_sub(user_id, ch['ch_id']):
                success_count += 1
                supabase.table("joined_speed_channels").upsert({"user_id": user_id, "ch_id": ch['id']}).execute()
        
        if success_count > 0:
            total_reward = success_count * reward_val
            update_user(user_id, {"balance": float(user['balance']) + total_reward})
            msg_alert = f"🎉 تم التحقق من {success_count} قناة بنجاح!\nأضيفت {total_reward:.4f} DOGE لرصيدك." if lang == 'ar' else f"🎉 Verified {success_count} channels!\nAdded {total_reward:.4f} DOGE."
            call_api("answerCallbackQuery", {"callback_query_id": cq['id'], "text": msg_alert, "show_alert": True})
            # تحديث الصفحة لإخفاء القنوات المكتملة
            process_callback({"id": "dummy", "message": cq['message'], "from": cq['from'], "data": f"open_ch_page_{page}"})
        else:
            call_api("answerCallbackQuery", {"callback_query_id": cq['id'], "text": "❌ لم تقم بالاشتراك في أي قناة من هذه الصفحة!", "show_alert": True})

    # ================= الإبلاغ عن قناة معطلة =================
    elif data.startswith("report_ch_"):
        ch_id = int(data.split("_")[2])
        ch_info = supabase.table("channels").select("*").eq("id", ch_id).execute().data
        if ch_info:
            send_msg(OWNER_ID, f"🚨 <b>بلاغ من مستخدم!</b>\n\n👤 المستخدم: <code>{user_id}</code>\n📢 القناة: {ch_info[0]['name']}\n🔗 الرابط: {ch_info[0]['url']}\n\n⚠️ المستخدم يبلغ أن الرابط لا يعمل أو هناك مشكلة في القناة. يرجى المراجعة والتعديل.")
            call_api("answerCallbackQuery", {"callback_query_id": cq['id'], "text": "✅ تم إرسال البلاغ للإدارة، شكراً لتعاونك!", "show_alert": True})

    # ================= واجهة المهام المتطورة =================
    elif data.startswith("open_task_page_"):
        page = int(data.split("_")[3])
        user = calculate_and_update_mining(user)
        all_tasks = supabase.table("shortlinks").select("*").execute().data
        
        if not all_tasks:
            call_api("answerCallbackQuery", {"callback_query_id": cq['id'], "text": "لا توجد مهام متاحة حالياً.", "show_alert": True})
            return
            
        total_pages = math.ceil(len(all_tasks) / 5)
        page_tasks = all_tasks[page*5 : (page+1)*5]
        
        msg_text = f"💰 <b>رصيدك:</b> <code>{user['balance']:.8f}</code> DOGE\n\n📋 <b>قائمة المهام السريعة:</b>" if lang == 'ar' else f"💰 <b>Balance:</b> <code>{user['balance']:.8f}</code> DOGE\n\n📋 <b>Quick Tasks:</b>"
        
        btns = []
        for t in page_tasks:
            c_res = supabase.table("claimed_tasks").select("claimed_at").eq("user_id", user_id).eq("task_id", t['id']).execute()
            if c_res.data and (now - c_res.data[0]['claimed_at'] < 86400):
                btns.append([{"text": f"✅ منجزة - {t['description']}", "callback_data": "ignore"}])
            else:
                # تصميم لطيف للمهمة
                btns.append([{"text": f"📌 {t['description']} (💰 {t['reward']} DOGE)", "callback_data": "ignore"}])
                btns.append([
                    {"text": "🔑 إدخال الرمز", "callback_data": f"enter_pass_{t['id']}"},
                    {"text": "🔗 افتح الرابط", "url": t['url']}
                ])
                
        nav_row = []
        if page > 0: nav_row.append({"text": "⬅️ السابق", "callback_data": f"open_task_page_{page-1}"})
        nav_row.append({"text": f"صفحة {page+1}/{total_pages}", "callback_data": "ignore"})
        if page < total_pages - 1: nav_row.append({"text": "التالي ➡️", "callback_data": f"open_task_page_{page+1}"})
        if nav_row: btns.append(nav_row)
        btns.append([{"text": "🔙 رجوع", "callback_data": "back_to_hub"}])

        edit_msg(chat_id, msg_id, msg_text, {"inline_keyboard": btns})
        call_api("answerCallbackQuery", {"callback_query_id": cq['id']})

    elif data.startswith("enter_pass_"):
        update_user(user_id, {"state": f"wait_pass_{data.split('_')[2]}"})
        call_api("answerCallbackQuery", {"callback_query_id": cq['id']})
        send_msg(chat_id, f"🔑 <b>أرسل الآن كلمة السر لهذه المهمة:</b>")

    # (باقي أوامر الإدارة كما هي في V16)
    elif data == "admin_real_stats" and user_is_admin:
        call_api("answerCallbackQuery", {"callback_query_id": cq['id']})
        total_users = len(supabase.table("users").select("user_id").execute().data)
        send_msg(chat_id, f"📈 <b>إحصائيات:</b>\nإجمالي المستخدمين: <code>{total_users}</code>")

# ================= ممر Vercel Serverless =================
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
            if body:
                data = json.loads(body.decode('utf-8'))
                if 'message' in data: process_message(data['message'])
                elif 'callback_query' in data: process_callback(data['callback_query'])
        except Exception: pass
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Active")
