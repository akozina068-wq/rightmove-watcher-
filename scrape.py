import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

RIGHTMOVE_URL = os.environ["RIGHTMOVE_URL"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEEN_FILE = "seen_ids.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
}


def load_seen():
    with open(SEEN_FILE) as f:
        return set(json.load(f))


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(seen), f, indent=2)


def fetch_listings(url):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("[data-testid^='propertyCard-']")

    listings = []
    seen_urls = set()

    for card in cards:
        link_el = card.select_one("a[href*='/properties/']")
        if not link_el or not link_el.get("href"):
            continue

        href = link_el["href"]
        prop_url = f"https://www.rightmove.co.uk{href}" if href.startswith("/") else href
        prop_url = prop_url.split("#")[0]

        if prop_url in seen_urls:
            continue
        seen_urls.add(prop_url)

        id_match = re.search(r"/properties/(\d+)", prop_url)
        if not id_match:
            continue
        prop_id = id_match.group(1)

        address_el = card.select_one("address")
        price_el = card.select_one("[class*='Price']")
        type_el = card.select_one("[class*='propertyType']")

        address = address_el.get_text(strip=True) if address_el else "Unknown address"
        price = price_el.get_text(strip=True) if price_el else "Price n/a"
        ptype = type_el.get_text(strip=True) if type_el else ""

        listings.append(
            {
                "id": prop_id,
                "url": prop_url,
                "address": address,
                "price": price,
                "type": ptype,
            }
        )

    return listings


def send_telegram(message):
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(
        api_url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=15,
    )
    resp.raise_for_status()


def main():
    first_run = not os.path.exists(SEEN_FILE) or os.path.getsize(SEEN_FILE) == 0

    if first_run:
        # Bootstrap: record everything currently live, but don't spam
        # Telegram with the entire backlog.
        with open(SEEN_FILE, "w") as f:
            json.dump([], f)

    seen = load_seen()
    listings = fetch_listings(RIGHTMOVE_URL)

    if first_run:
        seen = {l["id"] for l in listings}
        save_seen(seen)
        print(f"Initial sync: recorded {len(seen)} existing listings. No notifications sent.")
        return

    new_listings = [l for l in listings if l["id"] not in seen]

    if not new_listings:
        print("No new listings.")
    else:
        print(f"Found {len(new_listings)} new listing(s).")
        for l in new_listings:
            msg = (
                f"\U0001F3E0 <b>New listing</b>\n"
                f"{l['address']}\n"
                f"{l['price']} \u2014 {l['type']}\n"
                f"{l['url']}"
            )
            try:
                send_telegram(msg)
            except Exception as e:
                print(f"Failed to send Telegram message for {l['id']}: {e}", file=sys.stderr)

    seen.update(l["id"] for l in listings)
    save_seen(seen)


if __name__ == "__main__":
    main()
