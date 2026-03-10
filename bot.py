import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL
from lyricsgenius import Genius
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
genius_token = os.getenv("GENIUS_API")

app = Client("keira", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
pytg = PyTgCalls(app)

queues = {}      # chat_id: [(title, url, thumbnail), ...]
now_playing = {} # chat_id: title
admins = {your_telegram_user_id_here}  # Senin ID'ni koy (settings → data → user id)

def fancy(text, emoji="🎸"):
    return f"{emoji} **{text}** {emoji}"

@app.on_message(filters.command("start"))
async def start(_, msg: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Komutlar 💥", callback_data="help")],
        [InlineKeyboardButton("Keira GitHub 🔥", url="https://github.com/seninrepo/keira-music-bot")]
    ])
    await msg.reply(fancy("Keira uyandı! Efsane müzik vakti geldi 🌌\nGrup ekle, /play ile patlat!", "🌟"), reply_markup=buttons)

@app.on_message(filters.command("help"))
async def help_cmd(_, msg):
    txt = fancy("Keira Komutları (Efsane Mod):\n\n"
                "/play <isim/link> → Sıraya ekle / hemen çal 🎧\n"
                "/pause → Duraklat ⏸️\n"
                "/resume → Devam ▶️\n"
                "/skip → Atla ⏭️\n"
                "/stop → Bitir 🛑\n"
                "/playlist → Sıra 📜\n"
                "/lyrics <isim> → Sözler 📝\n"
                "/volume <0-200> → Ses ayarı 🔊\n"
                "/join → Sese gir (admin) 🔗\n"
                "/leave → Çık (admin) ❌")
    await msg.reply(txt)

@app.on_message(filters.command("play"))
async def play(_, msg: Message):
    chat_id = msg.chat.id
    query = " ".join(msg.command[1:]).strip()
    if not query:
        return await msg.reply(fancy("Ne çalayım piç? Şarkı/link ver!", "😤"))

    ydl_opts = {"format": "bestaudio/best", "quiet": True, "no_warnings": True, "extract_flat": False}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            if "http" in query:
                info = ydl.extract_info(query, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
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
        await pytg.join_group_call(
            chat_id,
            AudioPiped(url),
            stream_type=StreamType().local_stream
        )
        text = fancy(f"Şimdi patlıyor: {title} 🚀")
        if thumb:
            await app.send_photo(chat_id, thumb, caption=text)
        else:
            await app.send_message(chat_id, text)
    except Exception as e:
        await app.send_message(chat_id, fancy(f"Hata: {str(e)} 😡 Retry..."))
        await start_play(chat_id)  # retry

@pytg.on_stream_end()
async def next_play(_):
    chat_id = _.chat_id  # pytgcalls handler'da chat_id böyle gelir
    await start_play(chat_id)

# Diğer komutlar (pause, resume, skip, stop, volume, lyrics, playlist, join, leave vs.)
# ... (yer tasarrufu için kısalttım, tam hali istersen log at, uzatırım)

if __name__ == "__main__":
    app.start()
    pytg.start()
    print("Keira efsane modda online! 🔥")
    asyncio.get_event_loop().run_forever()
