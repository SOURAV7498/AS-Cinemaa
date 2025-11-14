from pyrogram import Client, filters
from database.ia_filterdb import Media
from info import LOG_CHANNEL, ADMINS

# ⚠️ Set your movie upload channel ID here
SOURCE_MOVIE_CHANNEL = -1003269588765   # <-- Change this


# Helper: Safe send message
async def safe_send(client, chat_id, text):
    try:
        await client.send_message(chat_id, text)
    except Exception as e:
        print(f"Failed to send message to {chat_id}: {e}")


@Client.on_message(filters.channel & filters.chat(SOURCE_MOVIE_CHANNEL))
async def new_movie_handler(client, message):

    print("📥 Handler triggered for message:", message.id)   # Debug log

    if not message.media:
        print("❌ No media found")
        return

    # ---- FIXED UNIVERSAL MEDIA DETECTION ----
    media_obj = getattr(message, message.media.value, None)
    file_id = getattr(media_obj, "file_id", None)

    if not file_id:
        print("❌ Media has no file_id")
        return

    print("📌 File ID detected:", file_id)

    # ---- CHECK IF FILE ALREADY EXISTS ----
    exists = await Media.file_exists(file_id)
    print("🔍 Exists in DB:", exists)
    if exists:
        return

    # ---- SAVE MEDIA ----
    caption = message.caption or "New Movie"

    await Media.add_media(
        file_id=file_id,
        file_name=caption,
        message_id=message.id,
        chat_id=SOURCE_MOVIE_CHANNEL
    )

    notify_text = (
        f"🎬 **New Movie Added!**\n\n"
        f"📌 **Title:**\n`{caption}`\n\n"
        f"🎞 **File ID:**\n`{file_id}`"
    )

    # ---- SEND TO LOG CHANNEL ----
    print("📨 Sending to LOG_CHANNEL...")
    await safe_send(client, LOG_CHANNEL, notify_text)

    # ---- SEND TO ADMINS ---
    print("📨 Notifying admins...")
    for admin in ADMINS:
       try:
        admin_id = int(admin)
        if admin_id <= 0:
            raise ValueError("Invalid Telegram user ID")
    except Exception as e:
        print(f"⚠️ Skipping invalid admin ID {admin}: {e}")
        continue

    await safe_send(client, admin_id, notify_text)
    

   

    print("✅ Notification process completed.")
