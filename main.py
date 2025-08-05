from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
from telegram import Update
import yt_dlp
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN environment variable is required")
    exit(1)

# 🟢 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
🎥 Video Downloader Bot

Привет! Я могу скачивать видео с различных платформ:
• YouTube
• Twitter/X
• Instagram
• TikTok 
• И многих других!

Просто отправь мне ссылку на видео, и я скачаю его для тебя.

Ограничения:
• Максимальный размер файла: 50MB
• Только публичные видео
    """
    await update.message.reply_text(welcome_message)

# 🟡 Обработка текстовых сообщений (ссылок)
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    # Проверяем, что это URL
    if not (url.startswith('http://') or url.startswith('https://')):
        await update.message.reply_text("Пожалуйста, отправь корректную ссылку на видео.")
        return

    await update.message.reply_text("Скачиваю видео, подожди немного...")

    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'best[filesize<50M]/best[ext=mp4]/best',
            'noplaylist': True,
        }

        # Создаем папку для загрузок
        os.makedirs('downloads', exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Проверяем размер файла
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    os.remove(filename)
                    await update.message.reply_text("Видео слишком большое (>50MB). Попробуйте другое видео.")
                    return

        # Отправляем файл
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                await update.message.reply_video(f, caption=f"Скачано с: {url}")
            
            # Удаляем файл после отправки
            os.remove(filename)
        else:
            await update.message.reply_text("Ошибка: не удалось скачать видео.")

    except Exception as e:
        error_message = f"Ошибка при скачивании: {str(e)}"
        if "Private video" in str(e):
            error_message = "Это приватное видео. Я могу скачивать только публичные видео."
        elif "Video unavailable" in str(e):
            error_message = "Видео недоступно или было удалено."
        elif "not supported" in str(e):
            error_message = "Эта платформа пока не поддерживается."
        
        await update.message.reply_text(error_message)

# 🔧 Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = """
🔧 Помощь

Поддерживаемые платформы:
• YouTube (youtube.com, youtu.be)
• Twitter/X (twitter.com, x.com)
• Instagram (instagram.com)
• TikTok (tiktok.com)
• Reddit (reddit.com)
• Facebook (facebook.com)
• Vimeo (vimeo.com)
• И многие другие!

Как использовать:
1. Отправь мне ссылку на видео
2. Жди, пока я скачаю видео
3. Получай готовый файл!

Команды:
/start - Начать работу
/help - Показать эту помощь

Ограничения:
• Размер файла: до 50MB
• Только публичные видео
• Видео без авторских ограничений
    """
    await update.message.reply_text(help_message)

# 🧠 Подключаем обработчики
if __name__ == "__main__":
    print("Starting Telegram Video Downloader Bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("Bot is running! Send /start to begin.")
    app.run_polling()
