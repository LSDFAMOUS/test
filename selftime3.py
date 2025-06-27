import os
import asyncio
import sqlite3
from telethon import TelegramClient, events, functions
from datetime import datetime

# API اطلاعات
api_id = 20814016
api_hash = '88124df5eaf897ca3f38a8d8a39f5eb8'
session_name = 'session'

# مسیر فایل فونت برای ذخیره
FONT_FILE = "current_font.txt"

# حذف فایل session اگر قفل شده باشه
def remove_locked_session():
    try:
        conn = sqlite3.connect(f'{session_name}.session')
        conn.execute('SELECT 1')
        conn.close()
    except sqlite3.OperationalError as e:
        if 'database is locked' in str(e).lower():
            print("⚠️ فایل session قفل شده. در حال حذف...")
            try:
                os.remove(f"{session_name}.session")
                os.remove(f"{session_name}.session-journal")
            except FileNotFoundError:
                pass
            return True
    return False

# ساخت کلاینت بدون پروکسی
def create_client():
    return TelegramClient(
        session_name,
        api_id,
        api_hash,
        use_ipv6=False
    )

# اگر قفل بود، حذف کن و کلاینت بساز
if remove_locked_session():
    print("✅ فایل session حذف شد. تلاش مجدد برای اجرا...")

client = create_client()

# ذخیره فونت در فایل
def set_font(font_name):
    with open(FONT_FILE, 'w', encoding='utf-8') as f:
        f.write(font_name)

# خواندن فونت از فایل
def get_font():
    if not os.path.exists(FONT_FILE):
        return "bold"
    with open(FONT_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

# تبدیل ساعت به فونت دلخواه
def to_styled_time(text, style):
    styles = {
        "bold": {'0': '𝟬', '1': '𝟭', '2': '𝟮', '3': '𝟯', '4': '𝟰',
                 '5': '𝟱', '6': '𝟲', '7': '𝟳', '8': '𝟴', '9': '𝟵', ':': ':'},
        "monospace": {'0': '𝟶', '1': '𝟷', '2': '𝟸', '3': '𝟹', '4': '𝟺',
                      '5': '𝟻', '6': '𝟼', '7': '𝟽', '8': '𝟾', '9': '𝟿', ':': ':'},
        "circle": {'0': '⓪', '1': '①', '2': '②', '3': '③', '4': '④',
                   '5': '⑤', '6': '⑥', '7': '⑦', '8': '⑧', '9': '⑨', ':': ':'},
        "fullwidth": {'0': '０', '1': '１', '2': '２', '3': '３', '4': '４',
                      '5': '５', '6': '６', '7': '７', '8': '８', '9': '９', ':': ':'},
        "small": {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
                  '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', ':': ':'},
        "double": {'0': '𝟘', '1': '𝟙', '2': '𝟚', '3': '𝟛', '4': '𝟜',
                   '5': '𝟝', '6': '𝟞', '7': '𝟟', '8': '𝟠', '9': '𝟡', ':': ':'},
        "superscript": {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
                        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', ':': ':'},
        "bubble": {'0': '⓿', '1': '⓵', '2': '⓶', '3': '⓷', '4': '⓸',
                   '5': '⓹', '6': '⓺', '7': '⓻', '8': '⓼', '9': '⓽', ':': ':'},
        "inverted": {'0': '🄀', '1': '🄁', '2': '🄂', '3': '🄃', '4': '🄄',
                     '5': '🄅', '6': '🄆', '7': '🄇', '8': '🄈', '9': '🄉', ':': ':'},
        "normal": {'0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
                   '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', ':': ':'}
    }
    mapping = styles.get(style, styles['bold'])
    return ''.join(mapping.get(c, c) for c in text)

# وضعیت سلف ساعت
base_name = "MeTi"
running = False
stop_signal = False

async def start_salf_saat(event=None):
    global running, stop_signal
    if running:
        if event:
            await event.reply("⏰ سلف ساعت از قبل فعاله.")
        return
    if event:
        await event.reply("✅ سلف ساعت فعال شد.")
    running = True
    stop_signal = False
    while not stop_signal:
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        current_font = get_font()
        styled_time = to_styled_time(time_str, current_font)
        new_name = f"{base_name} {styled_time}"
        me = await client.get_me()
        if me.first_name != new_name:
            await client(functions.account.UpdateProfileRequest(first_name=new_name))
        await asyncio.sleep(59)
    running = False
    print("❌ سلف ساعت متوقف شد.")

@client.on(events.NewMessage(chats="me"))
async def command_handler(event):
    global stop_signal
    cmd = event.raw_text.strip()

    if cmd == "تنظیم ساعت":
        await start_salf_saat(event)

    elif cmd == "خاموش ساعت":
        if not running:
            await event.reply("⚠️ سلف ساعت فعال نیست.")
        else:
            stop_signal = True
            await event.reply("❌ سلف ساعت غیرفعال شد.")

    elif cmd.startswith("تنظیم فونت ساعت"):
        parts = cmd.split(" ", 3)
        if len(parts) < 4:
            await event.reply("❌ لطفاً فونت را مشخص کن. مثال: تنظیم فونت ساعت bold")
            return
        font = parts[3].strip().lower()
        valid_fonts = ["bold", "monospace", "circle", "fullwidth", "small", "double", "superscript", "bubble", "inverted", "normal"]
        if font not in valid_fonts:
            await event.reply("⚠️ فونت نامعتبر. فونت‌های مجاز:\n" + ", ".join(valid_fonts))
            return
        set_font(font)
        await event.reply(f"✅ فونت ساعت تنظیم شد به: {font}")


# 💖 افزودن قابلیت قلب رنگی
@client.on(events.NewMessage(pattern='^قلب$'))
async def heart_colors(event):
    peer = event.chat_id
    msg = await client.send_message(peer, '❤️')
    hearts = ['🧡', '💛', '💚', '💙', '💜', '❤️']
    for heart in hearts:
        await asyncio.sleep(0.7)
        try:
            await client.edit_message(peer, msg.id, heart)
        except:
            pass

# اجرای نهایی
with client:
    client.run_until_disconnected()
