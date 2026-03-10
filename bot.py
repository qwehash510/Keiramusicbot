import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

app = Client(
    "KeiraMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

call = PyTgCalls(app)

ydl_opts = {
    "format": "bestaudio",
    "quiet": True
}

def search(query):
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        return info["url"], info["title"]

@app.on_message(filters.command("start"))
async def start(_, message):

    text = """
✨ **Keira Music Bot**

🎧 Telegram sesli sohbetinde müzik çalar.

Komutlar:

▶️ /oynat şarkı adı  
⏹ /durdur  
⏭ /geç  
⏸ /pause  
▶️ /resume  
📜 /komutlar
"""

    await message.reply(text)

@app.on_message(filters.command("komutlar"))
async def commands(_, message):

    text = """
🎧 **Keira Komutları**

▶️ /oynat → müzik başlatır  
⏸ /pause → müziği duraklatır  
▶️ /resume → devam ettirir  
⏭ /geç → sonraki şarkıya geçer  
⏹ /durdur → müziği kapatır
"""

    await message.reply(text)

@app.on_message(filters.command("oynat"))
async def play(_, message):

    if len(message.command) < 2:
        return await message.reply("🎧 Bir şarkı adı yaz.")

    query = " ".join(message.command[1:])

    url, title = search(query)

    chat_id = message.chat.id

    await call.join_group_call(
        chat_id,
        AudioPiped(url)
    )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏸ Duraklat", callback_data="pause"),
                InlineKeyboardButton("▶️ Devam", callback_data="resume")
            ],
            [
                InlineKeyboardButton("⏭ Geç", callback_data="skip"),
                InlineKeyboardButton("⏹ Durdur", callback_data="stop")
            ]
        ]
    )

    await message.reply(
        f"🎶 **Çalıyor:**\n{title}",
        reply_markup=buttons
    )

@app.on_callback_query()
async def controls(_, query):

    chat_id = query.message.chat.id

    if query.data == "pause":
        await call.pause_stream(chat_id)

    if query.data == "resume":
        await call.resume_stream(chat_id)

    if query.data == "skip":
        await query.message.reply("⏭ Şarkı atlandı.")

    if query.data == "stop":
        await call.leave_group_call(chat_id)

    await query.answer()

@app.on_message(filters.command("durdur"))
async def stop(_, message):
    await call.leave_group_call(message.chat.id)
    await message.reply("⏹ Müzik durduruldu.")

@app.on_message(filters.command("pause"))
async def pause(_, message):
    await call.pause_stream(message.chat.id)
    await message.reply("⏸ Müzik duraklatıldı.")

@app.on_message(filters.command("resume"))
async def resume(_, message):
    await call.resume_stream(message.chat.id)
    await message.reply("▶️ Müzik devam ediyor.")

app.start()
call.start()
asyncio.get_event_loop().run_forever()
