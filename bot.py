import json
import requests
import pycountry
from datetime import datetime
from bs4 import BeautifulSoup
import telebot
from telebot import types

# توكن بوت التيليجرام
API_TOKEN = '5966375685:AAEQO-MxUiW9Da7j3o1jQblK2GU-5keczm8'
bot = telebot.TeleBot(API_TOKEN)

# معرف مالك البوت
OWNER_ID = 5868423807  # تأكد من إزالة الاقتباسات حول الرقم

# معرف قناة الاشتراك الإجباري (مثال: @my_channel أو -1001234567890)
MANDATORY_CHANNEL = '@mish_ry'

# تخزين لغة المستخدم
user_languages = {}
subscribed_users = set()

def get_country_flag(country_code):
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if country:
            return f"{chr(127397 + ord(country_code[0]))}{chr(127397 + ord(country_code[1]))}"
        else:
            return "🏳️"  # علم أبيض كافتراضي في حالة عدم العثور على علم
    except Exception:
        return "🏳️"

def get_country_name(country_code):
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if country:
            return country.name
        else:
            return "Unknown"
    except Exception:
        return "Unknown"

class LordGivt:
    def __init__(self, username):
        self.username = username.lstrip('@')
        self.json_data = None
        self.send_request()

    def send_request(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0"
        }
        url = f"https://www.tiktok.com/@{self.username}"
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            script_tag = soup.find('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
            if script_tag:
                script_text = script_tag.text.strip()
                self.json_data = json.loads(script_text)["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]
            else:
                raise ValueError("Failed to find the script tag.")
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch data: {e}")
        except (AttributeError, json.JSONDecodeError, KeyError) as e:
            raise ValueError("Error parsing user data: " + str(e))

    def get_user_id(self):
        return str(self.json_data.get("user", {}).get("id", "Unknown"))

    def get_name(self):
        return self.json_data.get("user", {}).get("nickname", "Unknown")

    def get_profile_image(self):
        return self.json_data.get("user", {}).get("avatarLarger", None)

    def is_verified(self):
        return "✅ Yes" if self.json_data.get("user", {}).get("verified", False) else "❌ No"

    def is_private(self):
        return "🔒 Yes" if self.json_data.get("user", {}).get("privateAccount", False) else "🔓 No"

    def followers(self):
        return f"{self.json_data.get('stats', {}).get('followerCount', 'Unknown'):,}"

    def following(self):
        return f"{self.json_data.get('stats', {}).get('followingCount', 'Unknown'):,}"

    def user_create_time(self):
        try:
            url_id = int(self.get_user_id())
            binary = "{0:b}".format(url_id)
            bits = binary[:31]
            timestamp = int(bits, 2)
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return "Unknown"

    def last_change_name(self):
        try:
            time = self.json_data["user"].get("nickNameModifyTime", "0")
            return datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return "Unknown"

    def account_region(self):
        return self.json_data.get("user", {}).get("region", "Unknown")

    def video_count(self):
        return f"{self.json_data.get('stats', {}).get('videoCount', 'Unknown'):,}"

    def open_favorite(self):
        return "✅ Yes" if self.json_data.get("user", {}).get("openFavorite", False) else "❌ No"

    def see_following(self):
        return "✅ Yes" if self.json_data.get("user", {}).get("followingVisibility", "0") == "1" else "❌ No"

    def language(self):
        return self.json_data.get("user", {}).get("language", "Unknown")

    def heart_count(self):
        return f"{self.json_data.get('stats', {}).get('heart', 'Unknown'):,}"

    def get_country_flag(self):
        country_code = self.json_data.get("user", {}).get("region", "Unknown")
        return get_country_flag(country_code)

    def get_country_name(self):
        country_code = self.json_data.get("user", {}).get("region", "Unknown")
        return get_country_name(country_code)

    def output(self, lang='en'):
        account_url = f"https://www.tiktok.com/@{self.username}"
        country_flag = self.get_country_flag()
        country_name = self.get_country_name()
        if lang == 'ar':
            return (f"📜 **[احصل على معلومات @{self.username}]({account_url})**\n\n"
                    f"🔹 **معرف المستخدم**: `{self.get_user_id()}`\n"
                    f"🔹 **اللقب**: `{self.get_name()}`\n"
                    f"🔹 **موثوق**: `{self.is_verified()}`\n"
                    f"🔹 **حساب خاص**: `{self.is_private()}`\n"
                    f"🔹 **المتابعين**: `{self.followers()}`\n"
                    f"🔹 **المتابعين له**: `{self.following()}`\n"
                    f"🔹 **الإعجابات**: `{self.heart_count()}`\n"
                    f"🔹 **عدد الفيديوهات**: `{self.video_count()}`\n"
                    f"🔹 **فتح المفضلة**: `{self.open_favorite()}`\n"
                    f"🔹 **يمكن رؤية قائمة المتابعين**: `{self.see_following()}`\n"
                    f"🔹 **لغة المستخدم**: `{self.language()}`\n"
                    f"🔹 **تاريخ إنشاء الحساب**: `{self.user_create_time()}`\n"
                    f"🔹 **آخر تغيير لاسم المستخدم**: `{self.last_change_name()}`\n"
                    f"🔹 **منطقة الحساب**: `{self.account_region()}`\n"
                    f"🔹 **علم البلد**: {country_flag} {country_name}\n"
                    f"🔹 **رابط الحساب**: [رابط الحساب]({account_url})\n"
                    f"🔹 **رابط قناة البوت**: [قناة البوت](https://t.me/mish_ry)\n"
                    f"🔹 **رابط المطور**: [المطور](https://t.me/d_3_x)\n")
        else:
            return (f"📜 **[Get Info For @{self.username}]({account_url})**\n\n"
                    f"🔹 **UserID**: `{self.get_user_id()}`\n"
                    f"🔹 **Nickname**: `{self.get_name()}`\n"
                    f"🔹 **Verified**: `{self.is_verified()}`\n"
                    f"🔹 **Private Account**: `{self.is_private()}`\n"
                    f"🔹 **Followers**: `{self.followers()}`\n"
                    f"🔹 **Following**: `{self.following()}`\n"
                    f"🔹 **Likes**: `{self.heart_count()}`\n"
                    f"🔹 **Video Count**: `{self.video_count()}`\n"
                    f"🔹 **Open Favorite**: `{self.open_favorite()}`\n"
                    f"🔹 **Can See Following List**: `{self.see_following()}`\n"
                    f"🔹 **User Language**: `{self.language()}`\n"
                    f"🔹 **User Create Time**: `{self.user_create_time()}`\n"
                    f"🔹 **Last Nickname Change**: `{self.last_change_name()}`\n"
                    f"🔹 **Account Region**: `{self.account_region()}`\n"
                    f"🔹 **Country Flag**: {country_flag} {country_name}\n"
                    f"🔹 **Account Link**: [Account Link]({account_url})\n"
                    f"🔹 **Bot Channel**: [Bot Channel](https://t.me/mish_ry)\n"
                    f"🔹 **Developer**: [Developer](https://t.me/d_3_x)\n")

def is_user_subscribed(user_id):
    try:
        chat_member = bot.get_chat_member(MANDATORY_CHANNEL, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        # إذا حدث خطأ (مثل أن القناة خاصة ولا يمكن الوصول إليها)، نعيد False
        return False

def create_channel_button():
    # إنشاء زر يوجه المستخدم إلى القناة للاشتراك
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{MANDATORY_CHANNEL.replace('@', '')}")
    markup.add(btn)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        # إذا لم يكن المستخدم مشتركًا، إرسال رسالة تطلب الاشتراك
        bot.send_message(message.chat.id, "يرجى الاشتراك في القناة للاستمرار.", reply_markup=create_channel_button())
        return

    subscribed_users.add(user_id)
    
    if user_id == OWNER_ID:
        bot.send_message(OWNER_ID, "مرحباً مالك البوت! استخدم /admin للوصول إلى لوحة التحكم.")
    else:
        bot.send_message(OWNER_ID, f"دخل المستخدم: [{message.from_user.first_name}](tg://user?id={message.from_user.id})", parse_mode='Markdown')

    if user_id not in user_languages:
        markup = types.InlineKeyboardMarkup()
        btn_en = types.InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')
        btn_ar = types.InlineKeyboardButton("🇪🇬 العربية", callback_data='lang_ar')
        markup.add(btn_en, btn_ar)
        start_message = "• مرحبا عزيزي، اختر لغتك المفضلة."
        bot.send_message(message.chat.id, start_message, reply_markup=markup, parse_mode='Markdown')
    else:
        language = user_languages[user_id]
        send_language_welcome(message, language)

def send_language_welcome(message, language):
    if language == 'ar':
        start_message = (f"• مرحبا عزيزي [{message.from_user.first_name}](tg://user?id={message.from_user.id}).\n"
                         "• هذا بوت معلومات التيك توك.\n"
                         "• أرسل معرف الحساب وسأقوم بكشف كل معلومات الحساب.")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("📢 قناة البوت", url="https://t.me/mish_ry")
        markup.add(btn)
        bot.send_message(message.chat.id, start_message, reply_markup=markup, parse_mode='Markdown')
    else:
        start_message = (f"• Welcome dear [{message.from_user.first_name}](tg://user?id={message.from_user.id}).\n"
                         "• This is the TikTok info bot.\n"
                         "• Send the account ID and I will reveal all account information.")
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("📢 Bot Channel", url="https://t.me/mish_ry")
        markup.add(btn)
        bot.send_message(message.chat.id, start_message, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_selection(call):
    user_id = call.from_user.id
    language = call.data.split('_')[1]
    
    if language in ['en', 'ar']:
        user_languages[user_id] = language
        
        if language == 'ar':
            start_message = (f"• مرحبا عزيزي [{call.from_user.first_name}](tg://user?id={call.from_user.id}).\n"
                             "• هذا بوت معلومات التيك توك.\n"
                             "• أرسل معرف الحساب وسأقوم بكشف كل معلومات الحساب.")
        else:
            start_message = (f"• Welcome dear [{call.from_user.first_name}](tg://user?id={call.from_user.id}).\n"
                             "• This is the TikTok info bot.\n"
                             "• Send the account ID and I will reveal all account information.")
        
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("📢 Bot Channel", url="https://t.me/mish_ry")
        markup.add(btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=start_message, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    user_id = message.from_user.id
    if user_id == OWNER_ID:
        markup = types.InlineKeyboardMarkup()
        stats_btn = types.InlineKeyboardButton("📊 الإحصائيات", callback_data='stats')
        broadcast_btn = types.InlineKeyboardButton("📢 الإذاعة", callback_data='broadcast')
        markup.add(stats_btn, broadcast_btn)
        bot.send_message(OWNER_ID, "مرحباً بك في لوحة التحكم. اختر أحد الخيارات:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "ليس لديك الصلاحيات للوصول إلى هذه اللوحة.")

@bot.callback_query_handler(func=lambda call: call.data == 'stats')
def show_stats(call):
    if call.from_user.id == OWNER_ID:
        total_users = len(subscribed_users)
        bot.edit_message_text(f"📊 **الإحصائيات**\n\n🔸 **إجمالي المستخدمين:** `{total_users}`", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == 'broadcast')
def broadcast_message(call):
    if call.from_user.id == OWNER_ID:
        sent_msg = bot.send_message(OWNER_ID, "📢 أرسل الرسالة التي ترغب في إذاعتها:")
        bot.register_next_step_handler(sent_msg, send_broadcast)

def send_broadcast(message):
    if message.from_user.id == OWNER_ID:
        for user_id in subscribed_users:
            try:
                bot.send_message(user_id, message.text, parse_mode='Markdown')
            except Exception:
                continue
        bot.send_message(OWNER_ID, "📢 تم إرسال الرسالة بنجاح!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_id = message.from_user.id
    if not is_user_subscribed(user_id):
        # إذا لم يكن المستخدم مشتركًا، إرسال رسالة تطلب الاشتراك مع زر القناة
        bot.send_message(message.chat.id, "يرجى الاشتراك في القناة للاستمرار.", reply_markup=create_channel_button())
        return

    username = message.text.strip()
    if username.startswith('@'):
        username = username[1:]

    try:
        user_info = LordGivt(username)
        profile_image = user_info.get_profile_image()
        language = user_languages.get(user_id, 'en')
        if profile_image:
            bot.send_photo(message.chat.id, profile_image, caption=user_info.output(lang=language), parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, user_info.output(lang=language), parse_mode='Markdown')

        # إضافة لوحة أزرار أسفل الرسالة
        markup = types.InlineKeyboardMarkup()
        btn_channel = types.InlineKeyboardButton("📢 Bot Channel", url="https://t.me/mish_ry")
        btn_developer = types.InlineKeyboardButton("👤 Developer", url="https://t.me/d_3_x")
        markup.add(btn_channel, btn_developer)

        bot.send_message(message.chat.id, "For more info, visit the bot channel or contact the developer.", reply_markup=markup)
        
    except ValueError as e:
        error_message = str(e)
        language = user_languages.get(user_id, 'en')
        if language == 'ar':
            bot.send_message(message.chat.id, f"حدث خطأ: {error_message}")
        else:
            bot.send_message(message.chat.id, f"An error occurred: {error_message}")

# بدء البوت
bot.polling(none_stop=True)