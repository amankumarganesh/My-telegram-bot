import asyncio
import os
from threading import Thread
from flask import Flask
from gtts import gTTS
import moviepy.editor as mp
import replicate
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Render Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Render Web Service Keep-Alive Server
app_web = Flask(__name__)


@app_web.route("/")
def home():
    return "Valentine 3D Video Bot is Active on Render!"


def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)


# /start कमांड
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💖 **100% Non-Copyright 3D Valentine Video Bot** 💖\n\n"
        "मुझे कोई भी वैलेंटाइन शायरी, लव मैसेज या डायलॉग हिंदी में भेजें।\n"
        "मैं आपके लिए एक शानदार 3D वैलेंटाइन कैरेक्टर वीडियो तैयार करूँगा।"
    )


# टेक्स्ट मिलने पर Short / Long और Theme चुनना
async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["user_text"] = update.message.text

    keyboard = [
        [
            InlineKeyboardButton(
                "📱 Valentine Reel (9:16)", callback_data="ratio_9:16"
            ),
            InlineKeyboardButton(
                "🖥️ Valentine Long Video (16:9)", callback_data="ratio_16:9"
            ),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌹 **वीडियो का फॉर्मेट चुनें:**", reply_markup=reply_markup
    )


# Video Generation Function
async def process_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_text = context.user_data.get("user_text", "Happy Valentine's Day!")
    user_id = query.from_user.id
    aspect_ratio = "9:16" if query.data == "ratio_9:16" else "16:9"

    raw_video_path = f"raw_val_{user_id}.mp4"
    audio_path = f"val_audio_{user_id}.mp3"
    final_output_path = f"val_final_{user_id}.mp4"

    status_msg = await query.edit_message_text(
        "⏳ **3D Valentine वीडियो बन रहा है...**\n"
        "✨ 100% Original 3D Character Rendering\n"
        "🎙️ Hindi Love Voice-Over Creation\n"
        "कृपया 1 से 2 मिनट इंतज़ार करें..."
    )

    try:
        # 1. Hindi Voice जनरेट करना
        tts = gTTS(text=user_text, lang="hi", slow=False)
        tts.save(audio_path)

        # 2. 100% Non-Copyright 3D Valentine AI Prompt
        # इसमें Disney/Pixar/Marvel का नाम नहीं है ताकि कॉपीराइट स्ट्राइक न आए
        ai_prompt = (
            f"Original 3D animated character, cute romantic anime stylized avatar holding a glowing red heart, "
            f"Valentine's Day romantic setting, soft glowing pink and red lighting, falling rose petals, "
            f"Unreal Engine 5 render, 8k resolution, cinematic 3D CGI animation, expressive face, "
            f"dialogue theme: {user_text}"
        )

        # 3. Replicate Video API कॉल
        output = replicate.run(
            "minimax/video-01",
            input={
                "prompt": ai_prompt,
                "prompt_optimizer": True,
            },
        )

        # 4. वीडियो डाउनलोड करना
        video_res = requests.get(output)
        with open(raw_video_path, "wb") as f:
            f.write(video_res.content)

        # 5. Audio और Video को मर्ज करना
        video_clip = mp.VideoFileClip(raw_video_path)
        audio_clip = mp.AudioFileClip(audio_path)

        if audio_clip.duration > video_clip.duration:
            video_clip = video_clip.loop(duration=audio_clip.duration)
        else:
            video_clip = video_clip.set_duration(audio_clip.duration)

        final_video = video_clip.set_audio(audio_clip)
        final_video.write_videofile(
            final_output_path, codec="libx264", audio_codec="aac"
        )

        # 6. टेलीग्राम पर वीडियो भेजना
        with open(final_output_path, "rb") as video_file:
            await context.bot.send_video(
                chat_id=query.message.chat_id,
                video=video_file,
                caption=f"❤️ **Valentine 3D Video Ready!**\n\n💌 *{user_text}*",
            )

        await status_msg.delete()

    except Exception as e:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"❌ वीडियो बनाने में समस्या आई: {str(e)}",
        )

    # 7. टेम्प फाइल्स क्लीन करना
    finally:
        for file in [raw_video_path, audio_path, final_output_path]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except Exception:
                    pass


def main():
    # Flask Web सर्वर
    Thread(target=run_web).start()

    # Telegram Bot
    bot_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt)
    )
    bot_app.add_handler(CallbackQueryHandler(process_video))

    print("Valentine Bot Running...")
    bot_app.run_polling()


if __name__ == "__main__":
    main()
