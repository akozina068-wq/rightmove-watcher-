# Rightmove Watcher

Checks your Rightmove search every 15 min and pings you on Telegram the moment a new property matching your filters appears. First run is silent (just records what's already there) so you don't get 40 messages at once.

Heads up: Rightmove's terms technically prohibit scraping. Low-frequency personal use for your own house hunt is common and low-risk, but this is at your own risk — don't scale it up or share the data.

## Setup (10 min)

**1. Create the repo**
Push these files to a new GitHub repo, keeping the folder structure exactly as-is (`.github/workflows/watch.yml` must stay at that path).

**2. Make your Telegram bot**
- In Telegram, message `@BotFather` → `/newbot` → follow the prompts.
- It gives you a token like `123456789:ABCdefGhIJKlmNoPQRsTUvwxYZ`. Save it.

**3. Get your chat ID**
- Message your new bot anything (e.g. "hi").
- Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser.
- Find `"chat":{"id":123456789,...}` in the response — that number is your chat ID.

**4. Add repo secrets**
Repo → Settings → Secrets and variables → Actions → New repository secret. Add three:
- `RIGHTMOVE_URL` — your full Rightmove search URL (the one with your filters)
- `TELEGRAM_BOT_TOKEN` — from step 2
- `TELEGRAM_CHAT_ID` — from step 3

**5. Allow the workflow to commit**
Repo → Settings → Actions → General → Workflow permissions → select **Read and write permissions** → Save. (Needed so it can save which listings it's already notified you about.)

**6. Run it once manually**
Repo → Actions tab → "Rightmove Watcher" → Run workflow. This does the silent initial sync.

After that it runs itself every 15 minutes and only messages you about genuinely new listings.

## Changing your search

Just update the `RIGHTMOVE_URL` secret with a new search URL whenever your criteria change — no code changes needed.

## Adjusting frequency

Edit the cron line in `.github/workflows/watch.yml`. `*/15 * * * *` = every 15 min. Public repos get unlimited free Actions minutes; private repos get 2,000 free min/month, so every 15 min (~2,900 runs/month at a few seconds each) comfortably fits either way.
