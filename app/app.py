import re

from config import Settings
from converter import convert_to_mp3, encode_mp3_with_lame, get_mp3_metadata
from downloader import download_google_drive_file
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeAudio

client = TelegramClient(
    "bot", Settings.TELEGRAM_API_ID, Settings.TELEGRAM_API_HASH
).start(bot_token=Settings.TELEGRAM_BOT_TOKEN)


@client.on(events.NewMessage(pattern="/start"))
async def start(event: events.NewMessage.Event):
    await event.respond(
        "Send me a Google Drive link to a video file and I will convert it to MP3 for you!"
    )
    raise events.StopPropagation


@client.on(events.NewMessage)
async def handle_message(event: events.NewMessage.Event):
    text = event.raw_text.strip()
    video_file, ffmpeg_mp3_file, mp3_file = None, None, None

    gdrive_pat = re.compile(r"https?://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)/?")
    items = gdrive_pat.search(text)
    if not items:
        await event.respond("Please send a valid Google Drive video URL.")
        return
    url = items.group(0)

    try:
        # Download the video from Google Drive
        await event.respond("Downloading video from Google Drive...")
        video_file = download_google_drive_file(url)

        # Convert the video to mp3
        await event.respond("Converting to MP3...")
        ffmpeg_mp3_file = await convert_to_mp3(video_file)
        mp3_file = await encode_mp3_with_lame(ffmpeg_mp3_file)
        duration = await get_mp3_metadata(mp3_file)

        # Send the mp3 file back to the user
        await event.respond("Uploading MP3...")
        await client.send_file(
            event.chat_id,
            mp3_file,
            attributes=[
                DocumentAttributeAudio(
                    duration=int(duration),  # Duration of the audio in seconds
                    title=video_file.stem,  # Title of the track
                    performer=video_file.stem,  # Performer/Artist name
                )
            ],
        )
        if video_file and video_file.exists():
            video_file.unlink(missing_ok=True)
        if ffmpeg_mp3_file and ffmpeg_mp3_file.exists():
            ffmpeg_mp3_file.unlink(missing_ok=True)
        if mp3_file and mp3_file.exists():
            mp3_file.unlink(missing_ok=True)

    except Exception as e:
        await event.respond(f"An error occurred: {e}")
    finally:
        pass
        # if video_file and video_file.exists():
        #     video_file.unlink(missing_ok=True)
        # if ffmpeg_mp3_file and ffmpeg_mp3_file.exists():
        #     ffmpeg_mp3_file.unlink(missing_ok=True)
        # if mp3_file and mp3_file.exists():
        #     mp3_file.unlink(missing_ok=True)


# Start the bot
def main():
    Settings.config_logger()
    client.start()
    print("Bot is running...")
    client.run_until_disconnected()


if __name__ == "__main__":
    main()
