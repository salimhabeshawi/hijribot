import logging
import os
import threading
import http.server
import socketserver
from datetime import datetime

from hijridate import Hijri, Gregorian
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# =========================================================
# Configuration & Constants
# =========================================================

SERVICE_NAME = "hijribot"
DEFAULT_PORT = 10000
HEALTH_PATH = "/health"

# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(SERVICE_NAME)

# =========================================================
# Environment loading (local only)
# =========================================================

if os.getenv("RENDER") is None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

# =========================================================
# Minimal HTTP Server (Render Web Service requirement)
# =========================================================


def start_http_server() -> None:
    port = int(os.environ.get("PORT", DEFAULT_PORT))

    class HealthHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == HEALTH_PATH:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"ok")
            else:
                self.send_response(404)
                self.end_headers()

        def do_HEAD(self):
            if self.path == HEALTH_PATH:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *_):
            return  # Silence default HTTP logs

    with socketserver.TCPServer(("0.0.0.0", port), HealthHandler) as server:
        logger.info("HTTP health server listening on port %s", port)
        server.serve_forever()

# =========================================================
# Hijri Utilities
# =========================================================


def format_hijri_date(dt: datetime) -> str:
    g = Gregorian(dt.year, dt.month, dt.day)
    h = g.to_hijri()
    return f"{h.day} {h.month_name()} {h.year} AH"


def days_until_ramadan(dt: datetime) -> int:
    g_today = Gregorian(dt.year, dt.month, dt.day)
    h_today = g_today.to_hijri()

    past_ramadan = (
        h_today.month > 9
        or (h_today.month == 9 and h_today.day > 1)
    )

    target_year = h_today.year + 1 if past_ramadan else h_today.year
    ramadan_start_g = Hijri(target_year, 9, 1).to_gregorian()

    ramadan_start_dt = datetime(
        ramadan_start_g.year,
        ramadan_start_g.month,
        ramadan_start_g.day,
    )

    return (ramadan_start_dt.date() - dt.date()).days


def hijri_year_progress(dt: datetime) -> tuple[int, int, float, str]:
    g_today = Gregorian(dt.year, dt.month, dt.day)
    h_today = g_today.to_hijri()

    day_of_year = h_today.day
    for month in range(1, h_today.month):
        day_of_year += Hijri(h_today.year, month, 1).month_length()

    total_days = sum(
        Hijri(h_today.year, month, 1).month_length()
        for month in range(1, 13)
    )

    percent = (day_of_year / total_days) * 100
    filled = round((percent / 100) * 20)

    progress_bar = (
        f"{'█' * filled}"
        f"{'░' * (20 - filled)} "
        f"{percent:.1f}%"
    )

    return day_of_year, total_days, percent, progress_bar

# =========================================================
# Telegram Command Handlers
# =========================================================


NOW_MESSAGE_TEMPLATE = """
<b>🌙 Hijri Year Progress</b>
━━━━━━━━━━━━━━━━━━━━━━

<b>السلام عليكم ورحمة الله وبركاته</b>

📅 <u><b>Today:</b></u>
{hijri_date}

⏳ <u><b>Days until Ramadan:</b></u>
~{days_until_ramadan}

📈 <u><b>Year {hijri_year} progress:</b></u>

{progress_bar}

@hijriyear_bot
""".strip()


HELP_MESSAGE = """
<b>How to use Hijri Year Bot</b>
━━━━━━━━━━━━━━━━━━━━━━
• /now — Show today’s Hijri date, days until Ramadan, and year progress.
""".strip()


async def now_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    today = datetime.now()

    hijri_date = format_hijri_date(today)
    days_left = days_until_ramadan(today)
    _, _, _, progress_bar = hijri_year_progress(today)
    hijri_year = Gregorian(
        today.year,
        today.month,
        today.day,
    ).to_hijri().year

    message = NOW_MESSAGE_TEMPLATE.format(
        hijri_date=hijri_date,
        days_until_ramadan=days_left,
        hijri_year=hijri_year,
        progress_bar=progress_bar,
    )

    await update.message.reply_text(
        message,
        parse_mode="HTML",
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await update.message.reply_text(
        HELP_MESSAGE,
        parse_mode="HTML",
    )

# =========================================================
# Application Lifecycle Hooks
# =========================================================


async def on_startup(app: Application) -> None:
    logger.info("Telegram bot started and polling for updates.")


async def on_error(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logger.exception(
        "Unhandled error while processing update=%r",
        update,
    )

# =========================================================
# Main Entrypoint
# =========================================================


def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN environment variable is not set")

    # Start minimal HTTP server (Render requirement)
    threading.Thread(
        target=start_http_server,
        daemon=True,
    ).start()

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("now", now_command))
    application.add_handler(CommandHandler("help", help_command))

    application.post_init = on_startup
    application.add_error_handler(on_error)

    logger.info("Starting Telegram polling...")
    application.run_polling()

# =========================================================
# Entry
# =========================================================


if __name__ == "__main__":
    main()
