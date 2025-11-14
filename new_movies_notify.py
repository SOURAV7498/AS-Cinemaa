from pyrogram import Client, filters
from database.ia_filterdb import Media
from info import LOG_CHANNEL, ADMINS

# ⚠️ Set your movie upload channel ID here
SOURCE_MOVIE_CHANNEL = -1002837138676   # <-- Change this

@Client.on_message(filters.channel & filters.chat(SOURCE_MOVIE_CHANNEL))
async def new_movie_handler(client, message):

    if not message.media:
        return

    # Detect media type
    file_id = (
        message.video.file_id if message.video else
        message.document.file_id if message.document else
        message.audio.file_id if message.audio else
        None
    )

    if not file_id:
        return

    # Check if media exists
    exists = await Media.file_exists(file_id)
    if exists:
        return

    # Save the new media
    await Media.add_media(
        file_id=file_id,
        file_name=message.caption or "New Movie",
        message_id=message.id,
        chat_id=SOURCE_MOVIE_CHANNEL
    )

    # Notification message
    caption = message.caption or "No title available"
    notify_text = (
        f"🎬 **New Movie Added!**\n\n"
        f"📌 **Title:**\n`{caption}`\n\n"
        f"🎞 **File ID:**\n`{file_id}`"
    )

    # Send alert to log channel
    await client.send_message(LOG_CHANNEL, notify_text)

    # Notify admins
    for admin in ADMINS:
        try:
            await client.send_message(int(admin), notify_text)
        except:
            pass
