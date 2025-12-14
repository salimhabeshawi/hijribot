import logging
from datetime import datetime
from hijridate import Hijri, Gregorian
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("hijribot")

# Load environment variables from .env
load_dotenv()


def format_hijri_date(dt: datetime) -> str:
    g = Gregorian(dt.year, dt.month, dt.day)
    h: Hijri = g.to_hijri()  # convert Gregorian -> Hijri
    return f"{h.day} {h.month_name()} {h.year} AH"


def days_until_ramadan(dt: datetime) -> int:
    g_today = Gregorian(dt.year, dt.month, dt.day)
    h_today: Hijri = g_today.to_hijri()

    past_ramadan_start = (h_today.month > 9) or (
        h_today.month == 9 and h_today.day > 1)
    target_hijri_year = h_today.year + 1 if past_ramadan_start else h_today.year

    ramadan_start_g = Hijri(target_hijri_year, 9, 1).to_gregorian()
    ramadan_start_dt = datetime(
        ramadan_start_g.year, ramadan_start_g.month, ramadan_start_g.day)

    return (ramadan_start_dt.date() - dt.date()).days


def hijri_year_progress(dt: datetime) -> tuple[int, int, float, str]:
    g_today = Gregorian(dt.year, dt.month, dt.day)
    h_today: Hijri = g_today.to_hijri()

    day_of_year = h_today.day
    for m in range(1, h_today.month):
        day_of_year += Hijri(h_today.year, m, 1).month_length()

    total_days = sum(Hijri(h_today.year, m, 1).month_length()
                     for m in range(1, 13))
    percent = (day_of_year / total_days) * 100

    filled = round((percent / 100) * 20)
    bar = f"{'█' * filled}{'░' * (20 - filled)} {percent:.1f}%"

    return day_of_year, total_days, percent, bar


async def now_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info("Handling /now from user_id=%s username=%s",
                user.id if user else None, user.username if user else None)
    today = datetime.now()
    hijri_str = format_hijri_date(today)
    days_left = days_until_ramadan(today)
    _, _, _, year_bar = hijri_year_progress(today)
    hijri_year = Gregorian(today.year, today.month, today.day).to_hijri().year

    await update.message.reply_text(
        "<b>🌙 Hijri Year Progress</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>السلام عليكم ورحمة الله وبركاته</b>\n\n"
        f"📅 <u><b>Today:</b></u>\n{hijri_str}\n\n"
        f"⏳ <u><b>Days until Ramadan:</b></u> ~{days_left}\n\n"
        f"📈 <u><b>Year {hijri_year} progress:</b></u>\n\n{year_bar}\n\n"
        "@hijriyear_bot",
        parse_mode="HTML"
    )
    logger.info("Replied with Hijri date: %s, days_left=%s, year_bar=%s",
                hijri_str, days_left, year_bar)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "<b>How to use Hijri Year Bot</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "• /now — show today’s Hijri date, days until Ramadan, and year progress.\n",
        parse_mode="HTML",
    )


async def on_startup(app: Application) -> None:
    logger.info("Bot started and ready to receive updates.")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled error while processing update=%r", update)


def main():
    token = os.getenv("BOT_TOKEN")  # use BOT_TOKEN env var
    if not token:
        logger.error("BOT_TOKEN is not set.")
        raise RuntimeError("Please set BOT_TOKEN environment variable.")
    logger.info("Launching bot with BOT_TOKEN present.")

    app = Application.builder().token(token).build()

    # Command handlers
    app.add_handler(CommandHandler("now", now_command))
    app.add_handler(CommandHandler("help", help_command))

    # Startup and error handling
    app.post_init = on_startup
    app.add_error_handler(on_error)

    logger.info("Starting polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
