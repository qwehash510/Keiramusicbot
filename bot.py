import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from py_tgcalls import PyTgCalls, StreamType
from py_tgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL
from lyricsgenius import Genius
from dotenv import load_dotenv

# Python 3.14+ loop fix (gerekirse, Fly.io 3.11 kullanacağız)
try:
    asyncio.get_event_loop()
except RuntimeError as e:
    if "no current event loop" in str(e).lower():
        asyncio.set_event_loop(asyncio.new_event_loop())

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
genius_token = os.getenv("GENIUS_API")

app = Client("keira", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
pytg = PyTgCalls(app)

queues = {}          # chat_id: [(title, url, thumb)]
now_playing = {}     # chat_id: title

def fancy(text, emoji="🎸"):
    return f"{emoji} **{text}** {emoji}"

@app.on_message(filters.command("start"))
async def start(_, msg: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Komutlar 💥", callback_data="help")],
        [InlineKeyboardButton("Keira GitHub 🔥", url="https://github.com/qwehash510/Keiramusicbot")]
    ])
    await msg.reply(fancy("Keira uyandı! Müzik vakti geldi 🌌\nGrup ekle, /play ile patlat!", "🌟"), reply_markup=buttons)

@app.on_message(filters.command("help"))
async def help_cmd(_, msg):
    txt = fancy("Keira Efsane Komutlar:\n\n"
                "/play <isim/link> → Sıraya ekle / çal 🎧\n"
                "/pause → Duraklat ⏸️\n"
                "/resume → Devam ▶️\n"
                "/skip → Atla ⏭️\n"
                "/stop → Bitir 🛑\n"
                "/playlist → Sıra 📜\n"
                "/lyrics <isim> → Sözler 📝\n"
                "/volume <0-200> → Ses 🔊\n"
                "/join → Sese gir (admin) 🔗\n"
                "/leave → Çık (admin) ❌")
    await msg.reply(txt)

@app.on_message(filters.command("play"))
async def play(_, msg: Message):
    chat_id = msg.chat.id
    query = " ".join(msg.command[1:]).strip()
    if not query:
        return await msg.reply(fancy("Ne çalayım lan? Link veya isim ver! 😤"))

    ydl_opts = {"format": "bestaudio/best", "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query if "http" in query else f"ytsearch:{query}", download=False)
            if "entries" in info:
                info = info["entries"][0]
            url = info["url"]
            title = info["title"]
            thumb = info.get("thumbnail")
        except Exception as e:
            return await msg.reply(fancy(f"Patladı: {str(e)} 💣"))

    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append((title, url, thumb))

    await msg.reply(fancy(f"{title} sıraya girdi! 🔥", "🎵"))

    if chat_id not in now_playing:
        await start_play(chat_id)

async def start_play(chat_id):
    if not queues.get(chat_id):
        now_playing.pop(chat_id, None)
        return

    title, url, thumb = queues[chat_id].pop(0)
    now_playing[chat_id] = title

    try:
        await pytg.join_group_call(chat_id, AudioPiped(url), stream_type=StreamType().local_stream)
        text = fancy(f"Şimdi patlıyor: {title} 🚀")
        if thumb:
            await app.send_photo(chat_id, thumb, caption=text)
        else:
            await app.send_message(chat_id, text)
    except Exception as e:
        await app.send_message(chat_id, fancy(f"Hata: {str(e)} 😡 Retry..."))
        await start_play(chat_id)

# Diğer komutlar (pause, resume, skip, stop, volume, lyrics, playlist, join, leave, ban vs.) buraya ekle
# Örnek pause:
@app.on_message(filters.command("pause"))
async def pause(_, msg):
    try:
        await pytg.pause_stream(msg.chat.id)
        await msg.reply(fancy("Duraklatıldı! ⏸️"))
    except:
        await msg.reply(fancy("Çalmıyor ki! 🤷"))

# ... kalan komutları önceki kodundan kopyala, hepsi aynı çalışır

if __name__ == "__main__":
    app.start()
    pytg.start()
    print("Keira efsane modda online! 🔥")
    asyncio.get_event_loop().run_forever()
