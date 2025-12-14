# Hijri Year Bot

A Telegram bot that shows today’s Hijri date, countdown to the coming Ramadan, and a progress bar for the current Hijri year.

## Features

- `/now` — Hijri date, days until next Ramadan, Hijri-year progress bar (with formatted message).
- `/help` — Quick usage guide.
- HTML formatting for a clean, bold header and structured sections.

## Requirements

- Python 3.10+
- Dependencies: `python-telegram-bot`, `hijridate`, `python-dotenv`
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

## Setup

1. Clone the repo and enter the folder:
   ```bash
   git clone https://github.com/yourname/hijribot.git
   cd hijribot
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Add your token to `.env`:
   ```env
   BOT_TOKEN=your-telegram-bot-token
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Commands

- `/now` — Display today’s Hijri date, days until Ramadan, and Hijri-year progress.
- `/help` — Show basic usage.

## Tests

If you use `pytest`:

```bash
python -m pytest
```

## Notes

- The bot uses HTML `parse_mode` for bold headers and structured text.
- Ensure your `.env` file is **not** committed (already ignored in `.gitignore`).

## License

MIT
