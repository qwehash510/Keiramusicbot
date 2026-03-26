import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserAdminInvalid, BadRequest

API_ID = 33188452
API_HASH = "ac4afbd122081956a173b16590c02609"
BOT_TOKEN = "8754618857:AAHtyt_lfuXGSnzW8IlpEstbNTR2WgV6ThQ"


OWNERS = {8508943513}

app = Client(
    "SikiciBanBotu",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)



async def start_bulk_ban(chat_username, limit, message):
    try:
        target_chat = await app.get_chat(chat_username)
    except:
        return await message.reply("❌ Grup bulunamadı. Username doğru mu?")

    await message.reply(f"🔍 Üyeler taranıyor...\n\nGrup: **{target_chat.title}**")

    members = []
    async for m in app.get_chat_members(target_chat.id):
        members.append(m.user.id)

    total = len(members)
    await message.reply(f"🚀 Grup üye sayısı: **{total}**\n"
                        f"Ban hedefi: **{limit}** kişi\n\nBaşlıyorum...")

    done = 0

    for uid in members:
        if done >= limit:
            break

        try:
            await app.ban_chat_member(target_chat.id, uid)
            done += 1
            print(f"{done}/{limit} → Banlandı: {uid}")
            await asyncio.sleep(0.00000000000000000001)

        except FloodWait as e:
            print(f"⏳ FloodWait: {e.x} saniye")
            await asyncio.sleep(e.x + 1)

        except UserAdminInvalid:
            print(f"❌ Admin banlanamaz: {uid}")

        except BadRequest:
            print(f"⚠ Banlanamadı: {uid}")

        except Exception as e:
            print(f"❗ Hata: {e}")
            await asyncio.sleep(1)

    await message.reply(f"✅ Bitti!\nBanlanan toplam üye: **{done}**")




@app.on_message(filters.private & filters.command("ban"))
async def ban_handler(client, message):

    if message.from_user.id not in OWNERS:
        return  

    try:
        cmd = message.text.split()
        chat_username = cmd[1]        
        limit = int(cmd[2])           
    except:
        return await message.reply("❌ Kullanım:\n`/ban @kullaniciadi 500`", quote=True)

    await start_bulk_ban(chat_username, limit, message)




app.run()
